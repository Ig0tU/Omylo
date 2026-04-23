import hashlib
import os
import re
from typing import List, Dict, Any, Optional

class SWDEngine:
    """
    Strict Write Discipline (SWD) Engine.
    Ensures that file modifications claimed by agents match the actual filesystem state.
    """
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir

    def get_file_hash(self, filepath: str) -> Optional[str]:
        """
        Calculates SHA-256 hash of a file.
        """
        full_path = os.path.join(self.root_dir, filepath)
        if not os.path.exists(full_path):
            return None
        with open(full_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    def parse_actions(self, output: str) -> List[Dict[str, Any]]:
        """
        Parses [FILE_ACTION] blocks from agent output.
        Format: [FILE_ACTION] OPERATION path [CONTENT] content [/CONTENT] [/FILE_ACTION]
        """
        actions = []
        pattern = r"\[FILE_ACTION\]\s*(CREATE|MODIFY|DELETE)\s+(\S+)(?:\s+\[CONTENT\](.*?)\[/CONTENT\])?\s*\[/FILE_ACTION\]"
        matches = re.finditer(pattern, output, re.DOTALL)
        for match in matches:
            operation = match.group(1)
            path = match.group(2)
            content = match.group(3) if match.group(3) else ""
            actions.append({
                "operation": operation,
                "path": path,
                "content": content.strip()
            })
        return actions

    def verify_and_execute(self, action: Dict[str, Any], dry_run: bool = False) -> Dict[str, Any]:
        """
        Verifies and executes a single file action.
        """
        operation = action["operation"]
        path = action["path"]
        content = action["content"]
        full_path = os.path.join(self.root_dir, path)

        pre_hash = self.get_file_hash(path)

        result = {
            "path": path,
            "operation": operation,
            "success": False,
            "error": None,
            "pre_hash": pre_hash,
            "post_hash": None
        }

        if dry_run:
            result["success"] = True
            return result

        try:
            if operation == "CREATE":
                if os.path.exists(full_path):
                    result["error"] = f"File {path} already exists."
                else:
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    with open(full_path, "w") as f:
                        f.write(content)
                    result["success"] = True
            elif operation == "MODIFY":
                if not os.path.exists(full_path):
                    result["error"] = f"File {path} does not exist."
                else:
                    with open(full_path, "w") as f:
                        f.write(content)
                    result["success"] = True
            elif operation == "DELETE":
                if not os.path.exists(full_path):
                    result["error"] = f"File {path} does not exist."
                else:
                    os.remove(full_path)
                    result["success"] = True

            result["post_hash"] = self.get_file_hash(path)
        except Exception as e:
            result["error"] = str(e)

        return result
