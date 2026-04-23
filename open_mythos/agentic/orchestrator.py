import re
import requests
from typing import List, Dict, Any, Optional, Callable
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
    def __init__(self, root_dir: str = ".", dry_run: bool = False, verbose: bool = False, web_mode: bool = False):
        self.root_dir = root_dir
        self.dry_run = dry_run
        self.verbose = verbose
        self.web_mode = web_mode
        self.matrix = AgentMatrix()
        self.swd = SWDEngine(root_dir)
        self.memory = MemoryManager(root_dir)
        self.metrics = MetricsManager(root_dir)
        self.tools = self.matrix.tools
        self.plan: List[Dict[str, str]] = []
        self.event_callback: Optional[Callable[[str, Any], None]] = None

    def _broadcast(self, event_type: str, data: Any):
        if self.event_callback:
            self.event_callback(event_type, data)
        if self.web_mode:
            try:
                requests.post("http://127.0.0.1:8000/api/stream/update", json={"type": event_type, "data": data}, timeout=1)
            except Exception:
                pass

    def execute_task(self, task_description: str):
        """
        Decomposes a task, recursive plans, and orchestrates agents to complete it.
        """
        self._broadcast("TASK_START", task_description)
        self.memory.log_action("TASK_START", task_description)

        # 0. Memory Retrieval (Knowledge Augmentation)
        self._broadcast("MEMORY_RETRIEVAL", task_description)
        past_knowledge = self.memory.search(task_description.split()[0]) # Simple heuristic
        context = f"Relevant past knowledge from memory: {past_knowledge}" if past_knowledge else ""

        # 1. Decomposition / Planning
        self.plan = self.decompose_task(task_description)
        self._broadcast("PLANNING", self.plan)
        self.memory.log_action("PLANNING", str(self.plan))

        if self.verbose:
            print(f"Plan created with {len(self.plan)} steps.")

        # 2. Execution Loop
        for i, step in enumerate(self.plan):
            if self.verbose:
                print(f"Executing step {i+1}/{len(self.plan)}: {step['description']}")

            output = self.execute_step(step, context)
            context = f"Previous step output: {output}"

        self._broadcast("TASK_COMPLETE", task_description)
        self.memory.log_action("TASK_COMPLETE", task_description)

        self.metrics.update_metrics(tokens=1000, cost=0.01)

    def decompose_task(self, task: str) -> List[Dict[str, str]]:
        """
        Decomposes a complex task into an orchestrated sequence of specialized agent actions.
        """
        self._broadcast("LATENT_REASONING_START", {"depth": 64})
        self._broadcast("DECOMPOSING", task)

        planner = self.matrix.spawn_agent(
            name="Archon",
            role="Grand Orchestrator",
            system_prompt=(
                "You are the Archon, the central intelligence of the Mythos Matrix. "
                "Decompose complex requests into a strategic execution graph. "
                "Format your response as a series of steps: "
                "STEP: [Description] | AGENT: [Specialized Role] | TOOLS: [Required Tools]"
            )
        )

        # In a real scenario, we'd loop here for 'latent reasoning'
        output = planner.run(f"Strategic decomposition for: {task}")

        steps = []
        # Support both STEP: format and the simpler fallback
        pattern = r"STEP:\s*(.*?)\s*\|\s*AGENT:\s*(.*?)(?:\s*\|\s*TOOLS:\s*(.*))?$"
        for line in output.split("\n"):
            line = line.strip()
            match = re.match(pattern, line)
            if match:
                steps.append({
                    "description": match.group(1).strip(),
                    "agent_role": match.group(2).strip(),
                    "tools": match.group(3).strip() if match.group(3) else "Any"
                })
            elif line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                # Fallback to simple parsing
                clean_line = line.lstrip("0123456789.-* ").strip()
                desc, role = clean_line.rsplit(" as ", 1) if " as " in clean_line else (clean_line, "Generalist")
                steps.append({"description": desc.strip(), "agent_role": role.strip()})

        if not steps:
            steps = [{"description": task, "agent_role": "Generalist"}]

        self._broadcast("LATENT_REASONING_COMPLETE", {"steps_generated": len(steps)})
        return steps

    def execute_step(self, step_info: Dict[str, str], context: str) -> str:
        """
        Assigns a step to an agent and handles its execution, including tool calls and latent loops.
        """
        self._broadcast("STEP_START", step_info)

        # 1. Spawn or Select Specialized Agent
        agent = self.matrix.spawn_agent(
            name=f"{step_info['agent_role']}Agent",
            role=step_info['agent_role'],
            system_prompt=(
                f"You are a {step_info['agent_role']}. "
                "Engage in deep reasoning before providing final actions. "
                "Use [FILE_ACTION] for filesystem changes and [TOOL_CALL] for utility usage."
            )
        )

        # 2. Latent Reasoning Loop (Simulated Recurrence)
        self._broadcast("LATENT_REASONING_START", {"agent": agent.name, "step": step_info['description']})

        # 3. Agent Run with context from previous steps
        task_with_context = f"TASK: {step_info['description']}\n\nCONTEXT FROM PREVIOUS STEPS: {context}"
        output = agent.run(task_with_context)

        self._broadcast("AGENT_OUTPUT", {"agent": agent.name, "output": output})
        self.memory.log_action("AGENT_RUN", f"Agent {agent.name} (Role: {agent.role}) output:\n{output}")

        # 3. Handle Tool Calls
        tool_calls = self.parse_tool_calls(output)
        for call in tool_calls:
            tool = self.tools.get_tool(call['name'])
            if tool:
                self._broadcast("TOOL_CALL", call)
                result = tool.execute(**call['params'])
                self._broadcast("TOOL_RESULT", result)
                self.memory.log_action("TOOL_RESULT", f"Tool {call['name']} result:\n{result}")

        # 4. SWD Verification
        actions = self.swd.parse_actions(output)
        for action in actions:
            self._broadcast("SWD_VERIFY_START", action)
            result = self.swd.verify_and_execute(action, dry_run=self.dry_run)
            self._broadcast("SWD_VERIFY_RESULT", result)
            self.memory.log_action("SWD_VERIFY", f"Action: {action['operation']} {action['path']}\nSuccess: {result['success']}\nError: {result['error']}")

        self._broadcast("STEP_COMPLETE", step_info)
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
