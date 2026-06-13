# layer_03/agent_loop.py
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_02.agent_loop import AgentLoop
from layer_02.tools import build_default_registry
from layer_03.context import ContextWindow
from layer_01.llm_client import SYSTEM_PROMPT

class ContextAwareAgentLoop(AgentLoop):
    def __init__(self, model: str = None, max_tokens: int = 6000):
        super().__init__(model)
        self.context = ContextWindow(max_tokens=max_tokens)

    def run(self, messages: list[dict]) -> str:
        # Trim before every LLM call
        trimmed = self.context.trim(messages)
        if len(trimmed) < len(messages):
            dropped = len(messages) - len(trimmed)
            print(f"  ✂️  trimmed {dropped} old message(s) to fit context window")
            # Mutate in place so the caller's list stays in sync
            messages[:] = trimmed

        stats = self.context.stats(messages)
        print(f"  📊 context: {stats['used']} / {stats['available']} tokens ({stats['pct']}%)")

        return super().run(messages)