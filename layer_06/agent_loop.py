# layer_06/agent_loop.py
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_05.agent_loop import PersistentAgentLoop
from layer_06.context import SummarizingContextWindow

class SummarizingAgentLoop(PersistentAgentLoop):
    def __init__(self, session_id: str, model: str | None = None, max_tokens: int = 6000):
        super().__init__(session_id, model, max_tokens)
        # Replace the plain context window with the summarizing one
        self.context = SummarizingContextWindow(max_tokens=max_tokens)

    def run(self, messages: list[dict]) -> str:
        # Try to summarize before running
        new_messages, did_summarize = self.context.maybe_summarize(messages)
        if did_summarize:
            messages[:] = new_messages  # mutate in place so caller sees the change

        return super().run(messages)