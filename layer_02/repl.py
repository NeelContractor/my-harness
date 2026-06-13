# layer_02/repl.py
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from layer_02.agent_loop import AgentLoop

def run_repl():
    agent = AgentLoop()
    messages = []

    print(f"🤖 Agent Harness — Layer 2 (Tools)")
    print(f"   Model: {agent.client.model}")
    print(f"   Tools: bash, read_file, write_file")
    print(f"   Commands: 'exit' to quit\n")

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

        messages.append({"role": "user", "content": user_input})
        print("Assistant: ", end="", flush=True)
        response = agent.run(messages)
        messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    run_repl()