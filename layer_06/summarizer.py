# layer_06/summarizer.py
import sys
import os
import json
import httpx
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_01.llm_client import LLMClient, SYSTEM_PROMPT

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'layer_01', '.env'))

SUMMARIZE_PROMPT = """You are summarizing a conversation between a user and an AI assistant.
Produce a concise summary (3-6 sentences) covering:
- What the user wanted to accomplish
- What actions were taken (tools called, files created, commands run)
- Key outcomes and current state
- Any important facts, preferences, or constraints mentioned

Be specific and factual. Do not editorialize."""

class Summarizer:
    def __init__(self, model: str | None = None):
        self.client = LLMClient(model) if model else LLMClient()

    def summarize(self, messages: list[dict]) -> str:
        """Summarize a list of messages into a compact paragraph."""
        # Format messages into readable text for the summarizer
        transcript = []
        for m in messages:
            role = m.get("role", "unknown")
            content = m.get("content") or ""

            if role == "tool":
                transcript.append(f"[Tool result]: {content[:300]}")
            elif m.get("tool_calls"):
                for tc in m["tool_calls"]:
                    name = tc["function"]["name"]
                    args = tc["function"]["arguments"]
                    transcript.append(f"[Assistant called tool]: {name}({args[:200]})")
            elif role in ("user", "assistant", "system"):
                if content:
                    transcript.append(f"[{role.capitalize()}]: {content[:500]}")

        transcript_text = "\n".join(transcript)

        payload = {
            "model": self.client.model,
            "messages": [
                {"role": "system", "content": SUMMARIZE_PROMPT},
                {"role": "user", "content": f"Summarize this conversation:\n\n{transcript_text}"}
            ],
            "stream": False,
        }

        api_key = os.getenv("OPENROUTER_API_KEY")
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

        return data["choices"][0]["message"]["content"].strip()