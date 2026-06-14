# layer_10/runner.py
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_09.agent_loop import WebAgentLoop
from layer_05.session import new_session_id, load_session, save_session

class TaskRunner:
    """
    Runs a single task (or interactive session) using the full agent stack.
    Designed for CLI use — no REPL loop, just run and return.
    """
    def __init__(
        self,
        session_id: str | None = None,
        model: str | None = None,
        max_tokens: int = 6000,
        verbose: bool = True,
    ):
        self.session_id = session_id or new_session_id()
        self.verbose = verbose

        # Load existing session if provided
        self.messages = []
        if session_id:
            try:
                self.messages = load_session(session_id)
                if verbose:
                    turns = len([m for m in self.messages if m["role"] == "user"])
                    print(f"  📂 Resumed session: {session_id} ({turns} previous turns)\n")
            except FileNotFoundError:
                if verbose:
                    print(f"  ⚠️  Session '{session_id}' not found — starting fresh\n")

        self.agent = WebAgentLoop(
            session_id=self.session_id,
            model=model,
            max_tokens=max_tokens,
        )

    def run(self, task: str) -> str:
        """Run a single task and return the response."""
        self.messages.append({"role": "user", "content": task})
        response = self.agent.run(self.messages)
        self.messages.append({"role": "assistant", "content": response})
        save_session(self.session_id, self.messages)
        return response

    def run_interactive(self):
        """Drop into an interactive REPL using the full agent stack."""
        print(f"  💬 Interactive mode (type 'exit' to quit)\n")
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye!")
                break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Bye!")
                break

            self.messages.append({"role": "user", "content": user_input})
            print("Assistant: ", end="", flush=True)
            response = self.agent.run(self.messages)
            self.messages.append({"role": "assistant", "content": response})
            print()