# layer_09/agent_loop.py
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_08.agent_loop import SandboxedAgentLoop
from layer_09.web import fetch_url, web_search
from layer_02.tools import Tool

class WebAgentLoop(SandboxedAgentLoop):
    def __init__(self, session_id: str, model: str | None = None, max_tokens: int = 6000):
        super().__init__(session_id, model, max_tokens)
        self._register_web_tools()

    def _register_web_tools(self):
        self.registry.register(Tool(
            name="web_fetch",
            description=(
                "Fetch the contents of a URL and return clean readable text. "
                "Use this to read documentation, articles, or any webpage."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The full URL to fetch (must start with http:// or https://)"
                    }
                },
                "required": ["url"]
            },
            fn=lambda url: fetch_url(url)
        ))

        self.registry.register(Tool(
            name="web_search",
            description=(
                "Search the web using DuckDuckGo. Returns titles, URLs, and snippets. "
                "Use this when you need current information or to find relevant URLs."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of results to return (default 5, max 10)",
                        "default": 5
                    }
                },
                "required": ["query"]
            },
            fn=lambda query, max_results=5: web_search(query, max_results)
        ))