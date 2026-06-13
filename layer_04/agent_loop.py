# layer_04/agent_loop.py
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_03.agent_loop import ContextAwareAgentLoop
from layer_04.memory import MemoryStore
from layer_01.llm_client import SYSTEM_PROMPT

MEMORY_SEARCH_THRESHOLD = 10  # below this count, just inject all memories

class MemoryAgentLoop(ContextAwareAgentLoop):
    def __init__(self, model: str = None, max_tokens: int = 6000):
        super().__init__(model, max_tokens)
        self.memory = MemoryStore()
        self._register_memory_tools()

    def _register_memory_tools(self):
        from layer_02.tools import Tool

        self.registry.register(Tool(
            name="save_memory",
            description="Save an important fact or piece of information to long-term memory for future sessions.",
            parameters={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The fact or info to remember"},
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags like ['user', 'project', 'preference']"
                    }
                },
                "required": ["content"]
            },
            fn=lambda content, tags=None: f"Memory saved (id={self.memory.save(content, tags)}): {content}"
        ))

        self.registry.register(Tool(
            name="search_memory",
            description="Search long-term memory for relevant facts from past sessions.",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to search for"}
                },
                "required": ["query"]
            },
            fn=lambda query: json.dumps(self.memory.search(query), indent=2) or "No memories found."
        ))

    def _get_relevant_memories(self, user_message: str) -> list[dict]:
        """Smart retrieval: inject all memories if few, search if many."""
        all_memories = self.memory.list_all(limit=100)
        if not all_memories:
            return []
        if len(all_memories) <= MEMORY_SEARCH_THRESHOLD:
            # Few memories — just inject all of them
            return all_memories[:5]
        # Many memories — use keyword search
        return self.memory.search(user_message, limit=3)

    def run(self, messages: list[dict]) -> str:
        last_user = next(
            (m["content"] for m in reversed(messages) if m["role"] == "user"),
            None
        )

        # Remove any previous memory injection before re-injecting
        messages[:] = [m for m in messages if not m.get("_memory_injection")]

        if last_user:
            relevant = self._get_relevant_memories(last_user)
            if relevant:
                memory_text = self.memory.format_for_prompt(relevant)
                print(f"  🧠 injecting {len(relevant)} memory/memories")
                messages.insert(0, {
                    "role": "system",
                    "content": memory_text,
                    "_memory_injection": True,
                })

        return super().run(messages)