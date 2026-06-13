# my-harness

A lightweight AI agent harness built in Python.

| Layer | What it does |
|--------|-------------|
| 1 — API Shell | Streaming LLM client + REPL |
| 2 — Tools | `bash`, `read_file`, `write_file` with an agentic loop |
| 3 — Context | Token counting + sliding window |
| 4 — Memory | SQLite persistent memory across sessions |
