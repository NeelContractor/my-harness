# layer_02/tools.py
import subprocess
import os
import json
from dataclasses import dataclass

@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    fn: callable

    def to_schema(self) -> dict:
        """Convert to OpenAI-compatible tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def schemas(self) -> list[dict]:
        return [t.to_schema() for t in self._tools.values()]

    def run(self, name: str, args: dict) -> str:
        tool = self.get(name)
        if not tool:
            return f"Error: unknown tool '{name}'"
        try:
            return tool.fn(**args)
        except Exception as e:
            return f"Error running tool '{name}': {e}"


# ── Built-in tools ──────────────────────────────────────────

def bash(command: str) -> str:
    """Run a shell command and return output."""
    result = subprocess.run(
        command, shell=True, capture_output=True, text=True, timeout=15
    )
    output = result.stdout.strip()
    error = result.stderr.strip()
    if error:
        return f"{output}\nSTDERR: {error}" if output else f"STDERR: {error}"
    return output or "(no output)"

def read_file(path: str) -> str:
    """Read a file and return its contents."""
    try:
        with open(os.path.expanduser(path), "r") as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: file not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"

def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(os.path.expanduser(path), "w") as f:
            f.write(content)
        return f"Written to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(Tool(
        name="bash",
        description="Run a bash command. Use for listing files, running scripts, checking system info, etc.",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "The shell command to run"}
            },
            "required": ["command"]
        },
        fn=bash,
    ))

    registry.register(Tool(
        name="read_file",
        description="Read the contents of a file.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["path"]
        },
        fn=read_file,
    ))

    registry.register(Tool(
        name="write_file",
        description="Write content to a file, creating it if it doesn't exist.",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to write to"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        },
        fn=write_file,
    ))

    return registry