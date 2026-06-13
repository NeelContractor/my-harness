# layer_01/llm_client.py
import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "openai/gpt-oss-120b:free"  

SYSTEM_PROMPT = "You are a helpful AI assistant built into a custom agent harness. You are NOT ChatGPT or any specific product — you are a general AI assistant."

class LLMClient:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

    def chat(self, messages: list[dict], stream: bool = True) -> str:
        """Send messages to the LLM. Returns the full response text."""
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            "stream": stream,
        }

        full_response = ""

        with httpx.Client() as client:
            with client.stream(
                "POST",
                f"{BASE_URL}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60,
            ) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if not line or line == "data: [DONE]":
                        continue
                    if line.startswith("data: "):
                        chunk = json.loads(line[6:])
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            print(delta, end="", flush=True)
                            full_response += delta

        print()  # newline after streaming ends
        return full_response