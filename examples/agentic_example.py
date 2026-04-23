from open_mythos.agentic.orchestrator import MythosOrchestrator
from open_mythos.agentic.base import Agent
from typing import Optional, Dict, Any

class CodeGenMockAgent(Agent):
    """
    A mock agent for demonstration purposes that simulates code generation.
    """
    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        if "Decompose" in self.system_prompt:
            return "1. Create main.py with basic math functions\n2. Create test_main.py"
        elif "main.py" in task:
            return """I will implement the math functions.
[FILE_ACTION] CREATE main.py [CONTENT]
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

if __name__ == "__main__":
    print(f"2 + 3 = {add(2, 3)}")
[/CONTENT] [/FILE_ACTION]
Done."""
        else:
            return "Task completed."

def run_example():
    print("--- OpenMythos Agentic Platform Example ---")
    # Initialize orchestrator in dry_run mode to avoid actual writes if preferred
    orchestrator = MythosOrchestrator(dry_run=False, verbose=True)

    # Inject mock agent to demonstrate the pipeline without model weights
    orchestrator.matrix.spawn_agent = lambda name, role, system_prompt: CodeGenMockAgent(name, role, system_prompt)

    print("\n[EX] Task: Create a math library")
    orchestrator.execute_task("Create a math library")

    print("\n--- Process Complete ---")
    print("Check MEMORY.md for the authoritative log of all actions.")

if __name__ == "__main__":
    run_example()
