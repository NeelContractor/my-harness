# layer_03/context.py
import json

# Rough token estimator: ~4 chars per token (good enough without tiktoken)
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)

def message_tokens(msg: dict) -> int:
    """Estimate tokens in a single message dict."""
    content = msg.get("content") or ""
    if isinstance(content, list):
        content = " ".join(p.get("text", "") for p in content)
    tool_calls = msg.get("tool_calls") or []
    tool_str = json.dumps(tool_calls) if tool_calls else ""
    return estimate_tokens(content + tool_str) + 4  # +4 for role overhead

def conversation_tokens(messages: list[dict]) -> int:
    return sum(message_tokens(m) for m in messages)


class ContextWindow:
    def __init__(self, max_tokens: int = 6000, reserve_tokens: int = 1000):
        # max_tokens: budget for conversation history
        # reserve_tokens: kept free for the model's response
        self.max_tokens = max_tokens
        self.reserve_tokens = reserve_tokens

    @property
    def available_tokens(self) -> int:
        return self.max_tokens - self.reserve_tokens

    def fits(self, messages: list[dict]) -> bool:
        return conversation_tokens(messages) <= self.available_tokens

    def trim(self, messages: list[dict]) -> list[dict]:
        """
        Drop oldest non-system messages until it fits.
        Always keeps the first message if it's a summary.
        """
        if self.fits(messages):
            return messages

        trimmed = list(messages)
        while trimmed and not self.fits(trimmed):
            # Never drop a summary marker at index 0
            start = 1 if trimmed and trimmed[0].get("_summary") else 0
            if len(trimmed) <= start + 1:
                break  # can't trim further
            trimmed.pop(start)

        return trimmed

    def stats(self, messages: list[dict]) -> dict:
        used = conversation_tokens(messages)
        return {
            "used": used,
            "available": self.available_tokens,
            "pct": round(used / self.available_tokens * 100, 1),
        }