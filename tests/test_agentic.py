import unittest
import os
import shutil
from open_mythos.agentic.orchestrator import MythosOrchestrator
from open_mythos.agentic.swd import SWDEngine
from open_mythos.agentic.memory import MemoryManager

class TestAgenticSystem(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_workspace"
        os.makedirs(self.test_dir, exist_ok=True)
        self.orchestrator = MythosOrchestrator(root_dir=self.test_dir)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_orchestrator_initialization(self):
        self.assertIsNotNone(self.orchestrator.matrix)
        self.assertIsNotNone(self.orchestrator.swd)
        self.assertIsNotNone(self.orchestrator.memory)

    def test_swd_parse_actions(self):
        output = """
        I will create a file.
        [FILE_ACTION] CREATE hello.txt [CONTENT] Hello World! [/CONTENT] [/FILE_ACTION]
        Done.
        """
        actions = self.orchestrator.swd.parse_actions(output)
        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["operation"], "CREATE")
        self.assertEqual(actions[0]["path"], "hello.txt")
        self.assertEqual(actions[0]["content"], "Hello World!")

    def test_swd_execute_action(self):
        action = {
            "operation": "CREATE",
            "path": "test.txt",
            "content": "Sample content"
        }
        result = self.orchestrator.swd.verify_and_execute(action)
        self.assertTrue(result["success"])

        full_path = os.path.join(self.test_dir, "test.txt")
        self.assertTrue(os.path.exists(full_path))
        with open(full_path, "r") as f:
            self.assertEqual(f.read(), "Sample content")

    def test_memory_logging(self):
        self.orchestrator.memory.log_action("TEST_EVENT", "This is a test")

        # Verify MEMORY.md
        memory_file = os.path.join(self.test_dir, "MEMORY.md")
        self.assertTrue(os.path.exists(memory_file))
        with open(memory_file, "r") as f:
            self.assertIn("TEST_EVENT", f.read())

        # Verify SQLite index
        results = self.orchestrator.memory.search("test")
        self.assertGreater(len(results), 0)
        self.assertIn("This is a test", results[0]["content"])

if __name__ == "__main__":
    unittest.main()
