# layer_04/memory.py
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "memory.db")

class MemoryStore:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with self._conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    tags TEXT DEFAULT '',
                    created_at TEXT NOT NULL
                )
            """)

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def save(self, content: str, tags: list[str] | None = None) -> int:
        """Save a memory. Returns the new row id."""
        tags_str = ",".join(tags or [])
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO memories (content, tags, created_at) VALUES (?, ?, ?)",
                (content, tags_str, now)
            )
            assert cur.lastrowid is not None
            return cur.lastrowid

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Simple keyword search across memory content."""
        words = query.lower().split()
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, content, tags, created_at FROM memories ORDER BY created_at DESC LIMIT 100"
            ).fetchall()

        results = []
        for row in rows:
            content_lower = row[1].lower()
            score = sum(1 for w in words if w in content_lower)
            if score > 0:
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "tags": row[2],
                    "created_at": row[3],
                    "score": score,
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def list_all(self, limit: int = 20) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, content, tags, created_at FROM memories ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [{"id": r[0], "content": r[1], "tags": r[2], "created_at": r[3]} for r in rows]

    def delete(self, memory_id: int) -> bool:
        with self._conn() as conn:
            cur = conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
            return cur.rowcount > 0

    def format_for_prompt(self, memories: list[dict]) -> str:
        if not memories:
            return ""
        lines = ["Relevant memories from past sessions:"]
        for m in memories:
            lines.append(f"- [{m['created_at'][:10]}] {m['content']}")
        return "\n".join(lines)