# layer_11/daemon.py
import sys
import os
import time
import threading

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_10.runner import TaskRunner
from layer_11.watcher import FileWatcher
from layer_11.reactions import get_reaction
from layer_05.session import new_session_id
from layer_08.sandbox import WORKSPACE_DIR

# Use a single persistent session for the whole daemon run
DAEMON_SESSION_ID = f"daemon_{new_session_id()}"

# Serialize agent calls — only one at a time
_agent_lock = threading.Lock()


def handle_change(filepath: str):
    """Called when a file is created or modified."""
    task = get_reaction(filepath)

    print(f"\n  🤖 Reacting to: {os.path.basename(filepath)}")
    print(f"  📋 Task: {task[:100]}...\n")

    # Run in a thread so watcher isn't blocked
    def run():
        with _agent_lock:
            runner = TaskRunner(
                session_id=DAEMON_SESSION_ID,
                verbose=True,
            )
            print("Assistant: ", end="", flush=True)
            runner.run(task)
            print()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()


def main():
    watch_dir = WORKSPACE_DIR
    os.makedirs(watch_dir, exist_ok=True)

    print("🤖 Agent Harness — Layer 11 (File Watcher)\n")
    print(f"   Watching: {watch_dir}")
    print(f"   Session:  {DAEMON_SESSION_ID}")
    print(f"   Reactions: .py → review, .txt → summarize, .md → suggestions")
    print(f"   Stop with: Ctrl+C\n")

    watcher = FileWatcher(watch_dir=watch_dir, on_change=handle_change)
    watcher.start()

    print("  ✅ Watcher running. Drop files into workspace/ to trigger reactions.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n  🛑 Stopping watcher...")
        watcher.stop()
        print("  Bye!")


if __name__ == "__main__":
    main()