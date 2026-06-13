# layer_02/agent_loop.py
import sys
import os
import json
import httpx
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_01.llm_client import LLMClient, SYSTEM_PROMPT
from layer_02.tools import ToolRegistry, build_default_registry

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'layer_01', '.env'))

class AgentLoop:
    def __init__(self, model: str = None, registry: ToolRegistry = None):
        self.client = LLMClient(model) if model else LLMClient()
        self.registry = registry or build_default_registry()

    def run(self, messages: list[dict]) -> str:
        """Run the agentic loop: call LLM, handle tool calls, return final response."""
        while True:
            response = self._call_llm(messages)
            
            # No tool calls → we're done
            if not response.get("tool_calls"):
                content = response.get("content") or ""
                print(content)
                return content

            # Handle tool calls
            tool_calls = response["tool_calls"]
            
            # Add assistant message with tool calls to history
            messages.append({"role": "assistant", "content": response.get("content"), "tool_calls": tool_calls})

            # Run each tool and collect results
            for tc in tool_calls:
                tool_name = tc["function"]["name"]
                tool_args = json.loads(tc["function"]["arguments"])

                print(f"\n  🔧 calling tool: {tool_name}({json.dumps(tool_args)})")
                result = self.registry.run(tool_name, tool_args)
                print(f"  📤 result: {result[:200]}{'...' if len(result) > 200 else ''}\n")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

    def _call_llm(self, messages: list[dict]) -> dict:
        """Call the LLM (non-streaming for tool use) and return the message dict."""
        import os
        api_key = os.getenv("OPENROUTER_API_KEY")
        
        payload = {
            "model": self.client.model,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            "tools": self.registry.schemas(),
            "tool_choice": "auto",
        }

        with httpx.Client() as http:
            resp = http.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=60,
            )
            resp.raise_for_status()
            data = resp.json()

        return data["choices"][0]["message"]