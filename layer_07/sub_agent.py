# layer_07/sub_agent.py
import sys
import os
import json
import httpx
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_02.tools import build_default_registry, ToolRegistry
from layer_01.llm_client import LLMClient

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'layer_01', '.env'))

class SubAgent:
    """
    A lightweight agent that runs a single focused task and returns a result.
    No memory, no session, no context trimming — just pure task execution.
    """
    def __init__(self, name: str, goal: str, model: str | None = None, registry: ToolRegistry | None = None):
        self.name = name
        self.goal = goal
        self.client = LLMClient(model) if model else LLMClient()
        self.registry = registry or build_default_registry()
        self.steps: list[str] = []  # log of what it did

    def run(self, task: str, max_steps: int = 10) -> str:
        """Run the sub-agent on a task. Returns the final result string."""
        print(f"\n  🤖 [{self.name}] starting: {task[:80]}")

        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a focused sub-agent. Your role: {self.goal}\n"
                    "Complete the task given to you using the tools available. "
                    "When done, respond with a clear summary of what you accomplished and the result."
                )
            },
            {"role": "user", "content": task}
        ]

        api_key = os.getenv("OPENROUTER_API_KEY")
        steps = 0

        while steps < max_steps:
            steps += 1
            payload = {
                "model": self.client.model,
                "messages": messages,
                "tools": self.registry.schemas(),
                "tool_choice": "auto",
                "stream": False,
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

            message = data["choices"][0]["message"]

            if not message.get("tool_calls"):
                result = message.get("content") or ""
                print(f"  ✅ [{self.name}] done in {steps} step(s)")
                self.steps.append(f"Result: {result[:100]}")
                return result

            # Handle tool calls
            messages.append({
                "role": "assistant",
                "content": message.get("content"),
                "tool_calls": message["tool_calls"]
            })

            for tc in message["tool_calls"]:
                tool_name = tc["function"]["name"]
                tool_args = json.loads(tc["function"]["arguments"])
                log = f"{tool_name}({list(tool_args.values())[0] if tool_args else ''})"
                print(f"    🔧 [{self.name}] {log[:80]}")
                self.steps.append(log)

                result = self.registry.run(tool_name, tool_args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": result,
                })

        return f"[{self.name}] reached max steps ({max_steps}) without completing."