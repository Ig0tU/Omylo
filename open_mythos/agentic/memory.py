import os
import sqlite3
import datetime
import hashlib
from typing import List, Dict, Any, Optional

class MemoryManager:
    """
    Manages agentic memory via MEMORY.md and a SQLite FTS5 index.
    The MEMORY.md file is the Sole Authority.
    """
    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.memory_file = os.path.join(self.root_dir, "MEMORY.md")
        self.db_file = os.path.join(self.root_dir, ".mythos_memory.db")
        self.init_db()

    def init_db(self):
        """
        Initializes the SQLite FTS5 index.
        """
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS memory_index USING fts5(content, timestamp, tags)")
        conn.commit()
        conn.close()

    def log_action(self, action_type: str, details: str, tags: List[str] = []):
        """
        Logs an action to MEMORY.md and the SQLite index.
        """
        timestamp = datetime.datetime.now().isoformat()
        tags_str = ",".join(tags)
        log_entry = f"## [{timestamp}] {action_type}\n\n{details}\n\nTags: {tags_str}\n\n---\n\n"

        # Append to MEMORY.md (Sole Authority)
        with open(self.memory_file, "a") as f:
            f.write(log_entry)

        # Index in SQLite
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO memory_index (content, timestamp, tags) VALUES (?, ?, ?)", (details, timestamp, tags_str))
        conn.commit()
        conn.close()

    def rebuild_index(self):
        """
        Rebuilds the SQLite index from the authoritative MEMORY.md file.
        """
        if not os.path.exists(self.memory_file):
            return

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memory_index")

        with open(self.memory_file, "r") as f:
            content = f.read()
            # Basic parsing of MEMORY.md entries
            entries = content.split("---")
            for entry in entries:
                if entry.strip():
                    cursor.execute("INSERT INTO memory_index (content, timestamp, tags) VALUES (?, ?, ?)", (entry.strip(), "", ""))

        conn.commit()
        conn.close()

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Searches the memory index. If query is "%", returns all entries.
        """
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if query == "%":
            cursor.execute("SELECT * FROM memory_index")
        else:
            cursor.execute("SELECT * FROM memory_index WHERE memory_index MATCH ?", (query,))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
