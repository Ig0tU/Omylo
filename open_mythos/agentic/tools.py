import os
import subprocess
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class Tool(ABC):
    """
    Abstract base class for all tools.
    """
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        pass

class FileSystemTool(Tool):
    @property
    def name(self) -> str:
        return "filesystem"

    @property
    def description(self) -> str:
        return "Reads, writes, and deletes files."

    def execute(self, operation: str, path: str, content: Optional[str] = None) -> str:
        # Implementation logic for file system operations
        return f"Executed {operation} on {path}"

class ShellTool(Tool):
    @property
    def name(self) -> str:
        return "shell"

    @property
    def description(self) -> str:
        return "Executes shell commands."

    def execute(self, command: str) -> str:
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"

class ToolRegistry:
    """
    Registry for managing and accessing tools.
    """
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        self.register_tool(FileSystemTool())
        self.register_tool(ShellTool())

    def register_tool(self, tool: Tool):
        self.tools[tool.name] = tool

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self.tools.values()]
