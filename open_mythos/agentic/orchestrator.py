from typing import List, Dict, Any, Optional
from .base import Agent
from .matrix import AgentMatrix
from .swd import SWDEngine
from .memory import MemoryManager

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
        self.plan: List[str] = []

    def execute_task(self, task_description: str):
        """
        Decomposes a task, recursive plans, and orchestrates agents to complete it.
        """
        self.memory.log_action("TASK_START", task_description)

        # 1. Decomposition / Planning
        self.plan = self.decompose_task(task_description)
        self.memory.log_action("PLANNING", "\n".join(self.plan))

        if self.verbose:
            print(f"Plan created: {self.plan}")

        # 2. Execution
        for i, step in enumerate(self.plan):
            if self.verbose:
                print(f"Executing step {i+1}/{len(self.plan)}: {step}")
            self.execute_step(step)

        self.memory.log_action("TASK_COMPLETE", task_description)

    def decompose_task(self, task: str) -> List[str]:
        """
        Decomposes a complex task into smaller, manageable steps using a high-effort agent.
        """
        planner = self.matrix.spawn_agent(
            name="Planner",
            role="Task Decomposer",
            system_prompt="Decompose the user's task into a numbered list of atomic steps. Each step should be clear and actionable."
        )

        output = planner.run(task)
        # Simple parsing of numbered list
        steps = []
        for line in output.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("-") or line.startswith("*")):
                steps.append(line.lstrip("0123456789.-* ").strip())

        if not steps:
            steps = [task] # Fallback to single step

        return steps

    def execute_step(self, step: str):
        """
        Assigns a step to an agent and handles its execution.
        """
        # 1. Select or Spawn Agent
        agent = self.matrix.spawn_agent(
            name="PrimaryAgent",
            role="General Purpose Assistant",
            system_prompt="You are a helpful assistant. Use [FILE_ACTION] blocks for file operations."
        )

        # 2. Agent Run
        output = agent.run(step)
        if self.verbose:
            print(f"Agent output: {output}")

        self.memory.log_action("AGENT_RUN", f"Agent {agent.name} output:\n{output}")

        # 3. SWD Verification
        actions = self.swd.parse_actions(output)
        for action in actions:
            if self.verbose:
                print(f"Verifying action: {action['operation']} {action['path']}")
            result = self.swd.verify_and_execute(action, dry_run=self.dry_run)
            self.memory.log_action("SWD_VERIFY", f"Action: {action['operation']} {action['path']}\nSuccess: {result['success']}\nError: {result['error']}")

            if not result["success"]:
                if self.verbose:
                    print(f"Action failed: {result['error']}")
                # Handle failure (e.g., correction turn or yield to human)
                pass
            elif self.verbose:
                print("Action executed successfully.")

    def chain_agents(self, task: str, agents: List[Agent]) -> str:
        """
        Chains multiple agents together for a complex task.
        """
        context = ""
        for agent in agents:
            context = agent.run(task, context={"previous_output": context})
        return context
