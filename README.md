# My Harness

A fully-featured AI agent harness built from scratch in Python — no LangChain, no frameworks, just clean layered code.

## What it does

- Talks to any LLM via OpenRouter (one API key, 100+ models)
- Calls tools: bash, read/write files, web search, web fetch
- Remembers facts across sessions via SQLite
- Saves and resumes full conversation sessions
- Summarizes old context instead of dropping it
- Spawns specialist sub-agents for complex tasks
- Runs code safely in Docker sandbox
- Watches folders and reacts to file changes autonomously
- Works as an interactive REPL or single-shot CLI command

## Setup

```bash
git clone <your-repo>
cd my-harness
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Add your OpenRouter API key to root `.env`:
```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

## Usage

```bash
# Single task
harness "explain how TCP works"

# With web search
harness "search for latest Python 3.14 features"

# Quiet mode (final answer only)
harness --quiet "write a haiku about Go"

# Interactive REPL
harness --interactive

# Resume a session
harness --session 2026-06-14_12-00-00 "continue where we left off"

# List all sessions
harness --list-sessions

# Delete a session
harness --delete-session 2026-06-14_12-00-00

# File watcher daemon
python3 layer_11/daemon.py
```

## Architecture

Each layer builds on the previous without modifying it:

| Layer | File | What it adds |
|-------|------|-------------|
| 1 | `layer_01/` | Streaming LLM client + REPL |
| 2 | `layer_02/` | Tool calling — bash, read_file, write_file |
| 3 | `layer_03/` | Token counting + sliding window trimming |
| 4 | `layer_04/` | SQLite persistent memory across sessions |
| 5 | `layer_05/` | Session save/resume as JSON files |
| 6 | `layer_06/` | Summarization when context fills up |
| 7 | `layer_07/` | Multi-agent orchestration with sub-agents |
| 8 | `layer_08/` | Docker sandboxed code execution |
| 9 | `layer_09/` | Web fetch + DuckDuckGo search |
| 10 | `layer_10/` | CLI mode with argparse |
| 11 | `layer_11/` | File watcher daemon |

## Project layout

```
my-harness/
├── harness.py          # CLI entrypoint
├── setup.py            # packaging
├── requirements.txt
├── workspace/          # agent's sandboxed working directory
├── sessions/           # saved conversation sessions (JSON)
├── layer_01/           # LLM client
│   ├── llm_client.py
│   └── repl.py
├── layer_02/           # tools
│   ├── tools.py
│   └── agent_loop.py
├── layer_03/           # context
│   ├── context.py
│   └── agent_loop.py
├── layer_04/           # memory
│   ├── memory.py
│   └── agent_loop.py
├── layer_05/           # sessions
│   ├── session.py
│   └── agent_loop.py
├── layer_06/           # summarization
│   ├── summarizer.py
│   ├── context.py
│   └── agent_loop.py
├── layer_07/           # multi-agent
│   ├── orchestrator.py
│   ├── sub_agent.py
│   └── agent_loop.py
├── layer_08/           # sandboxing
│   ├── sandbox.py
│   └── agent_loop.py
├── layer_09/           # web
│   ├── web.py
│   └── agent_loop.py
├── layer_10/           # CLI
│   ├── cli.py
│   └── runner.py
└── layer_11/           # file watcher
    ├── watcher.py
    ├── reactions.py
    └── daemon.py
```

## Extending

**Add a new tool:**
Edit `layer_02/tools.py`, register it in `build_default_registry()`.

**Add a new sub-agent specialist:**
Edit `layer_07/orchestrator.py`, add to `SPECIALISTS`.

**Add a new file reaction:**
Edit `layer_11/reactions.py`, add a new extension to `REACTIONS`.

**Switch models:**
```bash
harness --model anthropic/claude-3-5-haiku-20241022 "your task"
```

## Requirements

- Python 3.10+
- Docker (optional, for sandboxed code execution)
- OpenRouter API key (free tier works)