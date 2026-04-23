import argparse
import sys
from .orchestrator import MythosOrchestrator

def main():
    parser = argparse.ArgumentParser(description="OpenMythos Agentic CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start an interactive agentic session")
    chat_parser.add_argument("task", type=str, help="The task for the orchestrator")
    chat_parser.add_argument("--dry-run", action="store_true", help="Preview file changes without executing")
    chat_parser.add_argument("--verbose", action="store_true", help="Show detailed execution traces")

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

    # Instantiate orchestrator only when needed to avoid overhead
    orchestrator = MythosOrchestrator(dry_run=getattr(args, 'dry_run', False), verbose=getattr(args, 'verbose', False))

    if args.command == "chat":
        print(f"Starting orchestration for task: {args.task}")
        orchestrator.execute_task(args.task)
        print("Task execution completed.")
    elif args.command == "verify":
        print("Verifying codebase integrity...")
        # Get all memory entries
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
