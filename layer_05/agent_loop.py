# layer_05/agent_loop.py
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_04.agent_loop import MemoryAgentLoop
from layer_05.session import save_session

class PersistentAgentLoop(MemoryAgentLoop):
    def __init__(self, session_id: str, model: str | None = None, max_tokens: int = 6000):
        super().__init__(model, max_tokens)
        self.session_id = session_id

    def run(self, messages: list[dict]) -> str:
        response = super().run(messages)
        # Auto-save after every turn
        save_session(self.session_id, messages)
        return response