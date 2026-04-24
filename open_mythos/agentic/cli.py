import argparse
import sys
from .orchestrator import MythosOrchestrator
from .base import Agent
from typing import Optional, Dict, Any

class CodeGenMockAgent(Agent):
    """
    An impressive mock agent that produces high-quality, highly-reasoned code.
    """
    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        if "Archon" in self.name or "Decompose" in self.system_prompt:
            return """STEP: Design the core DistributedLock class with Redis-based TTL and atomic operations. | AGENT: Architect | TOOLS: FileSystem
STEP: Implement safety mechanisms: retry-on-failure, context manager support, and heartbeats. | AGENT: Engineer | TOOLS: Shell
STEP: Write a comprehensive unit test suite to verify re-entrancy and dead-lock prevention. | AGENT: Tester | TOOLS: pytest"""

        elif "DistributedLock" in task or "Design" in task:
            return """# Reasoning Process:
# 1. Selection of Redis as the backend for shared state across distributed nodes.
# 2. Use of SET with NX (Set-if-Not-Exists) and PX (Milliseconds TTL) for atomicity.
# 3. Lua scripting to ensure the 'Release' operation is atomic and only unlocks owned locks.
# 4. Context Manager pattern for guaranteed release.

[FILE_ACTION] CREATE dlock.py [CONTENT]
import uuid
import time
import redis
from typing import Optional
from contextlib import contextmanager

class DistributedLock:
    \"\"\"
    A production-grade distributed lock implementation using Redis.
    Provides mutual exclusion across multiple nodes with automatic expiration
    and atomic safety checks.
    \"\"\"
    def __init__(self, redis_client: redis.Redis, name: str, timeout: int = 10):
        self.redis = redis_client
        self.name = f"lock:{name}"
        self.timeout = timeout
        self.id = str(uuid.uuid4())

    def acquire(self, blocking: bool = True, wait_time: float = 0.1) -> bool:
        \"\"\"Attempts to acquire the lock atomically.\"\"\"
        while True:
            # PX: expire time in ms, NX: set only if not exists
            if self.redis.set(self.name, self.id, px=int(self.timeout * 1000), nx=True):
                return True
            if not blocking:
                return False
            time.sleep(wait_time)

    def release(self):
        \"\"\"Releases the lock using a Lua script to ensure atomicity.\"\"\"
        script = \"\"\"
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        \"\"\"
        self.redis.eval(script, 1, self.name, self.id)

    @contextmanager
    def context(self):
        \"\"\"Context manager for safe usage.\"\"\"
        acquired = self.acquire()
        try:
            yield acquired
        finally:
            self.release()
[/CONTENT] [/FILE_ACTION]
Distributed lock implementation complete with atomic Lua release and UUID-based ownership validation."""
        else:
            return "Task step completed successfully."

def main():
    parser = argparse.ArgumentParser(description="OpenMythos Agentic CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start an interactive agentic session")
    chat_parser.add_argument("task", type=str, help="The task for the orchestrator")
    chat_parser.add_argument("--dry-run", action="store_true", help="Preview file changes without executing")
    chat_parser.add_argument("--verbose", action="store_true", help="Show detailed execution traces")
    chat_parser.add_argument("--mock", action="store_true", help="Use mock agent for demo")
    chat_parser.add_argument("--provider", type=str, default="mythos", choices=["mythos", "openai", "gemini"], help="AI provider to use")
    chat_parser.add_argument("--api-key", type=str, help="API key for the provider")
    chat_parser.add_argument("--base-url", type=str, help="Base URL for OpenAI-compatible providers (LM Studio/Ollama)")
    chat_parser.add_argument("--model-name", type=str, help="Model name for the provider")

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

    orchestrator = MythosOrchestrator(
        dry_run=getattr(args, 'dry_run', False),
        verbose=getattr(args, 'verbose', False),
        web_port=getattr(args, 'port', 8000)
    )

    # Provider configuration
    provider = getattr(args, 'provider', 'mythos')
    api_key = getattr(args, 'api_key', None)
    base_url = getattr(args, 'base_url', None)
    model_name = getattr(args, 'model_name', None)

    if getattr(args, 'mock', False):
        orchestrator.matrix.spawn_agent = lambda name, role, system_prompt, **kwargs: CodeGenMockAgent(name, role, system_prompt)
    elif provider != "mythos":
        # Override spawn_agent to use the selected provider
        original_spawn = orchestrator.matrix.spawn_agent
        def provider_spawn(name, role, system_prompt, agent_type=provider, **kwargs):
            # Merge CLI args with specific agent kwargs
            spawn_kwargs = {
                "api_key": api_key or kwargs.get("api_key"),
                "base_url": base_url or kwargs.get("base_url"),
                "model_name": model_name or kwargs.get("model_name")
            }
            return original_spawn(name, role, system_prompt, agent_type=agent_type, **spawn_kwargs)
        orchestrator.matrix.spawn_agent = provider_spawn

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
