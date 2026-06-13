# layer_04/repl.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from layer_04.agent_loop import MemoryAgentLoop

def run_repl():
    agent = MemoryAgentLoop()
    messages = []

    print(f"🤖 Agent Harness — Layer 4 (Memory)")
    print(f"   Model: {agent.client.model}")
    print(f"   Tools: bash, read_file, write_file, save_memory, search_memory")
    print(f"   Memory: {agent.memory.db_path}")
    print(f"   Commands: 'exit' to quit, '/memories' to list all\n")

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
        if user_input.lower() == "/memories":
            all_mem = agent.memory.list_all()
            if not all_mem:
                print("  (no memories yet)\n")
            else:
                for m in all_mem:
                    print(f"  [{m['id']}] {m['created_at'][:10]} — {m['content']}")
            print()
            continue

        messages.append({"role": "user", "content": user_input})
        print("Assistant: ", end="", flush=True)
        response = agent.run(messages)
        messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    run_repl()