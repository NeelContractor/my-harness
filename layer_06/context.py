# layer_06/context.py
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_03.context import ContextWindow, conversation_tokens
from layer_06.summarizer import Summarizer

# How full the context must be before we summarize (80%)
SUMMARIZE_AT = 0.80

class SummarizingContextWindow(ContextWindow):
    def __init__(self, max_tokens: int = 6000, reserve_tokens: int = 1000):
        super().__init__(max_tokens, reserve_tokens)
        self.summarizer = Summarizer()

    def maybe_summarize(self, messages: list[dict]) -> tuple[list[dict], bool]:
        """
        If context is over SUMMARIZE_AT threshold, summarize the oldest
        messages and replace them with a summary block.
        Returns (new_messages, did_summarize).
        """
        used = conversation_tokens(messages)
        threshold = self.available_tokens * SUMMARIZE_AT

        if used <= threshold:
            return messages, False

        # Split: keep the newest 30% of messages fresh, summarize the rest
        keep_count = max(2, len(messages) // 3)
        to_summarize = messages[:-keep_count]
        to_keep = messages[-keep_count:]

        # Don't summarize if there's nothing meaningful to compress
        if len(to_summarize) < 2:
            return messages, False
        
        print(f"\n  📝 context at {round(used/self.available_tokens*100)}% — summarizing {len(to_summarize)} messages...")
        summary_text = self.summarizer.summarize(to_summarize)
        print(f"  ✅ summarized into {len(summary_text)} chars\n")

        summary_message = {
            "role": "system",
            "content": f"[CONVERSATION SUMMARY]\n{summary_text}",
            "_summary": True,
        }

        return [summary_message] + to_keep, True