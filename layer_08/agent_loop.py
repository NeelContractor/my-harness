# layer_08/agent_loop.py
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_07.agent_loop import MultiAgentLoop
from layer_08.sandbox import Sandbox, WORKSPACE_DIR
from layer_02.tools import Tool

class SandboxedAgentLoop(MultiAgentLoop):
    def __init__(self, session_id: str, model: str | None = None, max_tokens: int = 6000):
        super().__init__(session_id, model, max_tokens)
        self.sandbox = Sandbox()
        self._replace_bash_with_sandbox()
        self._patch_write_file()

    def _replace_bash_with_sandbox(self):
        if "bash" in self.registry._tools:
            del self.registry._tools["bash"]

        self.registry.register(Tool(
            name="bash",
            description=(
                f"Run a bash command in a sandboxed workspace ({WORKSPACE_DIR}). "
                f"Mode: {self.sandbox.mode}. "
                "Dangerous commands are blocked. Timeout: 15s."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "The shell command to run"}
                },
                "required": ["command"]
            },
            fn=lambda command: self.sandbox.run_bash(command)
        ))

        self.registry.register(Tool(
            name="run_python",
            description="Execute Python code in the sandboxed workspace and return the output.",
            parameters={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"}
                },
                "required": ["code"]
            },
            fn=lambda code: self.sandbox.run_python(code)
        ))

    def _patch_write_file(self):
        """Make write_file default to workspace directory."""
        if "write_file" in self.registry._tools:
            del self.registry._tools["write_file"]

        def write_file_workspace(path: str, content: str) -> str:
            # If path is not absolute, put it in workspace
            if not os.path.isabs(path):
                path = os.path.join(WORKSPACE_DIR, path)
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return f"Written to {path}"

        self.registry.register(Tool(
            name="write_file",
            description=f"Write content to a file in the workspace ({WORKSPACE_DIR}). Use relative paths.",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path (e.g. 'test.txt')"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            },
            fn=write_file_workspace
        ))