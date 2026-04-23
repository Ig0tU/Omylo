import argparse
import sys
from .orchestrator import MythosOrchestrator
from .base import Agent
from typing import Optional, Dict, Any

class CodeGenMockAgent(Agent):
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

def main():
    parser = argparse.ArgumentParser(description="OpenMythos Agentic CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start an interactive agentic session")
    chat_parser.add_argument("task", type=str, help="The task for the orchestrator")
    chat_parser.add_argument("--dry-run", action="store_true", help="Preview file changes without executing")
    chat_parser.add_argument("--verbose", action="store_true", help="Show detailed execution traces")
    chat_parser.add_argument("--mock", action="store_true", help="Use mock agent for demo")

    # Web command
    web_parser = subparsers.add_parser("web", help="Start the Mythos Latent WebUI")
    web_parser.add_argument("--port", type=int, default=8000, help="Backend port")
    web_parser.add_argument("--mock", action="store_true", help="Use mock agent for demo")

    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify codebase against memory")

    # Dream command
    dream_parser = subparsers.add_parser("dream", help="Compress and optimize memory")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show session budget and cost stats")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "web":
        print(f"Starting Mythos Latent WebUI on port {args.port}...")
        from .web.server import start_server, get_orchestrator
        if args.mock:
             orch = get_orchestrator()
             orch.matrix.spawn_agent = lambda name, role, system_prompt: CodeGenMockAgent(name, role, system_prompt)
        start_server(port=args.port)
        return

    orchestrator = MythosOrchestrator(dry_run=getattr(args, 'dry_run', False), verbose=getattr(args, 'verbose', False))
    if getattr(args, 'mock', False):
        orchestrator.matrix.spawn_agent = lambda name, role, system_prompt: CodeGenMockAgent(name, role, system_prompt)

    if args.command == "chat":
        print(f"Starting orchestration for task: {args.task}")
        orchestrator.execute_task(args.task)
        print("Task execution completed.")
    elif args.command == "verify":
        print("Verifying codebase integrity...")
        entries = orchestrator.memory.search("%")
        reports = orchestrator.swd.verify_codebase(entries)
        for report in reports:
            status_icon = "✅" if report["status"] == "VERIFIED" else "⚠️" if report["status"] == "DRIFT" else "❌"
            print(f"{status_icon} {report['status']}: {report['path']} - {report['detail']}")
    elif args.command == "dream":
        print("Performing memory dreaming/compression...")
        orchestrator.memory.rebuild_index()
    elif args.command == "stats":
        print("Displaying budget and cost statistics...")
        stats = orchestrator.metrics.get_stats()
        print(f"Total Sessions: {stats['sessions']}")
        print(f"Total Tokens: {stats['total_tokens']:,}")
        print(f"Total Estimated Cost: ${stats['total_cost']:.4f}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
