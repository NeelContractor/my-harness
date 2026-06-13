# my-harness

A lightweight AI agent harness built in Python.

| Layer | What it does |
|--------|-------------|
| 1 — API Shell | Streaming LLM client + REPL |
| 2 — Tools | `bash`, `read_file`, `write_file` with an agentic loop |
| 3 — Context | Token counting + sliding window |
| 4 — Memory | SQLite persistent memory across sessions |


### The layers currently implemented are:

- **Layer 1** — A multi-provider streaming client (talks to Anthropic/OpenAI) + a REPL to chat with it
- **Layer 2** — Tool calling (give your agent the ability to run functions)
- **Layer 3** — Context management (token counting, summarization so it doesn't run out of memory)
- **Layer 4** — Long-term memory via SQLite 