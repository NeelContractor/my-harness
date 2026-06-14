# layer_07/agent_loop.py
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_06.agent_loop import SummarizingAgentLoop
from layer_07.orchestrator import Orchestrator

class MultiAgentLoop(SummarizingAgentLoop):
    def __init__(self, session_id: str, model: str | None = None, max_tokens: int = 6000):
        super().__init__(session_id, model, max_tokens)
        self.orchestrator = Orchestrator(model=model)

        # Register spawn_agent as a tool the main agent can call
        for tool in self.orchestrator.tools():
            self.registry.register(tool)