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
        return "Reads, writes, and deletes files. Operations: read, write, list, delete."

    def execute(self, operation: str, path: str, content: Optional[str] = None) -> str:
        try:
            if operation == "read":
                with open(path, "r") as f:
                    return f.read()
            elif operation == "write":
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w") as f:
                    f.write(content or "")
                return f"Successfully wrote to {path}"
            elif operation == "list":
                if os.path.isdir(path):
                    return "\n".join(os.listdir(path))
                return f"Error: {path} is not a directory."
            elif operation == "delete":
                if os.path.exists(path):
                    os.remove(path)
                    return f"Successfully deleted {path}"
                return f"Error: {path} does not exist."
            else:
                return f"Error: Unknown operation {operation}"
        except Exception as e:
            return f"Error: {str(e)}"

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

class DynamicPythonTool(Tool):
    def __init__(self, name: str, description: str, code: str):
        self._name = name
        self._description = description
        self.code = code

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def execute(self, **kwargs) -> Any:
        # Warning: Direct execution of agent-generated code.
        # In a production environment, this should be sandboxed.
        namespace = {}
        try:
            exec(self.code, namespace)
            if "run" in namespace:
                return namespace["run"](**kwargs)
            return "Error: Dynamic tool must define a 'run' function."
        except Exception as e:
            return f"Error executing dynamic tool {self.name}: {str(e)}"

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

    def create_dynamic_tool(self, name: str, description: str, code: str):
        tool = DynamicPythonTool(name, description, code)
        self.register_tool(tool)
        return f"Tool '{name}' successfully registered and added to the matrix."

    def get_tool(self, name: str) -> Optional[Tool]:
        return self.tools.get(name)

    def list_tools(self) -> List[Dict[str, str]]:
        return [{"name": t.name, "description": t.description} for t in self.tools.values()]
