import re
from typing import List, Dict, Any, Optional
from .base import Agent
from .matrix import AgentMatrix
from .swd import SWDEngine
from .memory import MemoryManager
from .tools import ToolRegistry
from .metrics import MetricsManager

class MythosOrchestrator:
    """
    The "God-in-a-app" orchestrator that coordinates a matrix of agents.
    """
    def __init__(self, root_dir: str = ".", dry_run: bool = False, verbose: bool = False):
        self.root_dir = root_dir
        self.dry_run = dry_run
        self.verbose = verbose
        self.matrix = AgentMatrix()
        self.swd = SWDEngine(root_dir)
        self.memory = MemoryManager(root_dir)
        self.metrics = MetricsManager(root_dir)
        self.tools = self.matrix.tools
        self.plan: List[Dict[str, str]] = []

    def execute_task(self, task_description: str):
        """
        Decomposes a task, recursive plans, and orchestrates agents to complete it.
        """
        self.memory.log_action("TASK_START", task_description)

        # 1. Decomposition / Planning
        self.plan = self.decompose_task(task_description)
        self.memory.log_action("PLANNING", str(self.plan))

        if self.verbose:
            print(f"Plan created with {len(self.plan)} steps.")

        # 2. Execution Loop
        context = ""
        for i, step in enumerate(self.plan):
            if self.verbose:
                print(f"Executing step {i+1}/{len(self.plan)}: {step['description']}")

            output = self.execute_step(step, context)
            context = f"Previous step output: {output}"

        self.memory.log_action("TASK_COMPLETE", task_description)

        # Update session metrics (simplified)
        self.metrics.update_metrics(tokens=1000, cost=0.01)

    def decompose_task(self, task: str) -> List[Dict[str, str]]:
        """
        Decomposes a complex task into smaller, manageable steps using a high-effort agent.
        """
        planner = self.matrix.spawn_agent(
            name="Planner",
            role="Task Decomposer",
            system_prompt="Decompose the user's task into a list of atomic steps. For each step, provide a 'description' and specify the 'agent_role' (e.g., Coder, Reviewer, Researcher) best suited for it. Output as a clear list."
        )

        output = planner.run(task)

        # Enhanced parsing
        steps = []
        lines = output.split("\n")
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                # Try to extract description and role
                clean_line = line.lstrip("0123456789.-* ").strip()
                if " as " in clean_line:
                    desc, role = clean_line.rsplit(" as ", 1)
                else:
                    desc, role = clean_line, "Generalist"
                steps.append({"description": desc.strip(), "agent_role": role.strip()})

        if not steps:
            steps = [{"description": task, "agent_role": "Generalist"}]

        return steps

    def execute_step(self, step_info: Dict[str, str], context: str) -> str:
        """
        Assigns a step to an agent and handles its execution, including tool calls.
        """
        # 1. Spawn or Select Specialized Agent
        agent = self.matrix.spawn_agent(
            name=f"{step_info['agent_role']}Agent",
            role=step_info['agent_role'],
            system_prompt=f"You are a {step_info['agent_role']}. Use [FILE_ACTION] blocks for file operations and [TOOL_CALL] for tool usage."
        )

        # 2. Agent Run with context from previous steps
        task_with_context = f"{step_info['description']}\n\n{context}"
        output = agent.run(task_with_context)

        if self.verbose:
            print(f"Agent ({agent.role}) output received.")

        self.memory.log_action("AGENT_RUN", f"Agent {agent.name} (Role: {agent.role}) output:\n{output}")

        # 3. Handle Tool Calls
        tool_calls = self.parse_tool_calls(output)
        for call in tool_calls:
            tool = self.tools.get_tool(call['name'])
            if tool:
                result = tool.execute(**call['params'])
                self.memory.log_action("TOOL_RESULT", f"Tool {call['name']} result:\n{result}")

        # 4. SWD Verification
        actions = self.swd.parse_actions(output)
        for action in actions:
            result = self.swd.verify_and_execute(action, dry_run=self.dry_run)
            self.memory.log_action("SWD_VERIFY", f"Action: {action['operation']} {action['path']}\nSuccess: {result['success']}\nError: {result['error']}")

        return output

    def parse_tool_calls(self, output: str) -> List[Dict[str, Any]]:
        """
        Parses [TOOL_CALL] blocks from agent output.
        """
        calls = []
        pattern = r"\[TOOL_CALL\]\s*(\w+)\s+(.*?)\[/TOOL_CALL\]"
        matches = re.finditer(pattern, output, re.DOTALL)
        for match in matches:
            name = match.group(1)
            params_str = match.group(2).strip()
            params = {}
            param_matches = re.finditer(r"(\w+)=(['\"]?)(.*?)\2(?:\s|$)", params_str)
            for p_match in param_matches:
                params[p_match.group(1)] = p_match.group(3)
            calls.append({"name": name, "params": params})
        return calls
