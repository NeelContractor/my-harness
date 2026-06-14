# layer_10/cli.py
import argparse
import sys
import os

# Find the harness root whether running locally or as installed package
HARNESS_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if HARNESS_ROOT not in sys.path:
    sys.path.insert(0, HARNESS_ROOT)
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_05.session import list_sessions, delete_session
from layer_10.runner import TaskRunner

def format_sessions(sessions: list[dict]):
    if not sessions:
        print("  No sessions found.")
        return
    print(f"\n  {'#':<4} {'Session ID':<25} {'Date':<20} {'Turns':<6} Preview")
    print(f"  {'-'*80}")
    for i, s in enumerate(sessions, 1):
        date = s["updated_at"][:16].replace("T", " ")
        print(f"  {i:<4} {s['session_id']:<25} {date:<20} {s['message_count']:<6} {s['preview'][:30]}")
    print()

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="harness",
        description="🤖 Agent Harness — AI agent with tools, memory, and web access",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python3 harness.py "what is the weather in Tokyo"
  python3 harness.py "write and test a quicksort in python"
  python3 harness.py --interactive
  python3 harness.py --session 2026-06-14_12-00-00 "continue the task"
  python3 harness.py --list-sessions
  python3 harness.py --delete-session 2026-06-14_12-00-00
        """
    )

    parser.add_argument(
        "task",
        nargs="?",
        help="Task to run (if omitted, enters interactive mode)"
    )
    parser.add_argument(
        "--session", "-s",
        metavar="SESSION_ID",
        help="Resume a specific session by ID"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Start an interactive REPL session"
    )
    parser.add_argument(
        "--list-sessions", "-l",
        action="store_true",
        help="List all saved sessions"
    )
    parser.add_argument(
        "--delete-session",
        metavar="SESSION_ID",
        help="Delete a session by ID"
    )
    parser.add_argument(
        "--model", "-m",
        metavar="MODEL",
        help="Override the LLM model (e.g. openai/gpt-4o)"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress tool call logs, only show final response"
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=6000,
        metavar="N",
        help="Context window token limit (default: 6000)"
    )

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    # ── --list-sessions ──────────────────────────────────────
    if args.list_sessions:
        sessions = list_sessions()
        format_sessions(sessions)
        return

    # ── --delete-session ─────────────────────────────────────
    if args.delete_session:
        if delete_session(args.delete_session):
            print(f"  ✅ Deleted session: {args.delete_session}")
        else:
            print(f"  ❌ Session not found: {args.delete_session}")
        return

    # ── No task and no --interactive → show help ─────────────
    if not args.task and not args.interactive:
        parser.print_help()
        return

    print(f"\n🤖 Agent Harness\n")

    # Suppress output in quiet mode by redirecting tool logs
    if args.quiet:
        # Monkey-patch print to filter tool call lines
        original_print = print
        def quiet_print(*a, **kw):
            text = " ".join(str(x) for x in a)
            # Only suppress the tool/context log lines
            if any(text.startswith(prefix) for prefix in ["  🔧", "  📤", "  📊", "  🧠", "  ✂️", "  📝", "  ✅ summarized"]):
                return
            original_print(*a, **kw)
        import builtins
        builtins.print = quiet_print

    runner = TaskRunner(
        session_id=args.session,
        model=args.model,
        max_tokens=args.max_tokens,
    )

    # ── Interactive mode ──────────────────────────────────────
    if args.interactive or not args.task:
        runner.run_interactive()
        return

    # ── Single task mode ──────────────────────────────────────
    print(f"  Task: {args.task}\n")
    print("Assistant: ", end="", flush=True)
    runner.run(args.task)
    print(f"\n  💾 Session: {runner.session_id}\n")