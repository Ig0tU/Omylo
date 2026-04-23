from open_mythos.agentic.orchestrator import MythosOrchestrator
from open_mythos.agentic.base import Agent
from typing import Optional, Dict, Any

class CodeGenMockAgent(Agent):
    """
    An impressive mock agent that produces high-quality, highly-reasoned code.
    """
    def run(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        if "Decompose" in self.system_prompt:
            return """1. Design the core DistributedLock class with Redis-based TTL and atomic operations.
2. Implement safety mechanisms: retry-on-failure, context manager support, and heartbeats.
3. Write a comprehensive unit test suite to verify re-entrancy and dead-lock prevention."""

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

def run_example():
    print("--- OpenMythos Agentic Platform: Impressive CodeGen Example ---")
    orchestrator = MythosOrchestrator(dry_run=False, verbose=True)

    # Inject impressive mock agent
    orchestrator.matrix.spawn_agent = lambda name, role, system_prompt: CodeGenMockAgent(name, role, system_prompt)

    print("\n[EX] Task: Implement a robust distributed locking system")
    orchestrator.execute_task("Implement a robust distributed locking system")

    print("\n--- Process Complete ---")
    print("Check MEMORY.md for the authoritative log and dlock.py for the produced code.")

if __name__ == "__main__":
    run_example()
