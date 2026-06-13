# layer_01/repl.py
from llm_client import LLMClient

def run_repl():
    client = LLMClient()
    messages = []

    print(f"🤖 Agent Harness — Layer 1")
    print(f"   Model: {client.model}")
    print(f"   Commands: 'exit' to quit, '/model <name>' to switch model\n")

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
        if user_input.startswith("/model "):
            new_model = user_input[7:].strip()
            client.model = new_model
            print(f"  ✅ Switched to model: {new_model}\n")
            continue

        messages.append({"role": "user", "content": user_input})

        print("Assistant: ", end="", flush=True)
        response = client.chat(messages)

        messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    run_repl()