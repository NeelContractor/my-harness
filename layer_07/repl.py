# layer_07/repl.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from layer_05.session import list_sessions, load_session, new_session_id, delete_session
from layer_07.agent_loop import MultiAgentLoop

def pick_session() -> tuple[str, list[dict]]:
    sessions = list_sessions()
    if not sessions:
        print("  No previous sessions. Starting new.\n")
        return new_session_id(), []

    print("  Previous sessions:")
    print(f"  {'#':<4} {'Date':<20} {'Turns':<6} Preview")
    print(f"  {'-'*60}")
    for i, s in enumerate(sessions[:10], 1):
        date = s["updated_at"][:16].replace("T", " ")
        print(f"  {i:<4} {date:<20} {s['message_count']:<6} {s['preview']}")
    print(f"\n  [N] New session")

    while True:
        choice = input("\n  Choose session (number or N): ").strip()
        if choice.upper() == 'N' or choice.lower() == '/new':
            return new_session_id(), []
        try:
            idx = int(choice) - 1
            sid = sessions[idx]["session_id"]
            msgs = load_session(sid)
            print(f"\n  ✅ Resumed: {sid}\n")
            return sid, msgs
        except (IndexError, ValueError):
            print("  Invalid choice.")

def run_repl():
    print("🤖 Agent Harness — Layer 7 (Multi-Agent)\n")

    session_id, messages = pick_session()
    agent = MultiAgentLoop(session_id=session_id)

    print(f"   Model: {agent.client.model}")
    print(f"   Session: {session_id}")
    print(f"   Sub-agents: researcher, coder, reviewer, executor")
    print(f"   Commands: 'exit', '/new', '/sessions'\n")

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
        if user_input.lower() == '/new':
            session_id = new_session_id()
            agent.session_id = session_id
            messages.clear()
            print(f"  ✅ New session: {session_id}\n")
            continue
        if user_input.lower() == '/sessions':
            for s in list_sessions():
                date = s["updated_at"][:16].replace("T", " ")
                print(f"  {date}  {s['message_count']} turns  —  {s['preview']}")
            print()
            continue

        messages.append({"role": "user", "content": user_input})
        print("Assistant: ", end="", flush=True)
        response = agent.run(messages)
        messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    run_repl()