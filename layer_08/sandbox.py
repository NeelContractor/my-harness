# layer_08/sandbox.py
import subprocess
import os
import tempfile

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
WORKSPACE_DIR = os.path.join(PROJECT_DIR, 'workspace')

BLOCKED_COMMANDS = [
    "rm -rf /",
    "mkfs",
    "dd if=",
    ":(){:|:&};:",
    "chmod 777 /",
    "curl | sh",
    "wget | sh",
    "> /dev/sda",
]

BLOCKED_PREFIXES = [
    "sudo",
    "su ",
]

def _ensure_workspace():
    os.makedirs(WORKSPACE_DIR, exist_ok=True)

def _is_dangerous(command: str) -> bool:
    cmd_lower = command.lower().strip()
    for blocked in BLOCKED_COMMANDS:
        if blocked in cmd_lower:
            return True
    for prefix in BLOCKED_PREFIXES:
        if cmd_lower.startswith(prefix):
            return True
    return False

def _docker_available() -> bool:
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True, timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def run_in_docker(command: str, timeout: int = 15) -> str:
    """Run a command inside Docker with only the workspace folder mounted."""
    _ensure_workspace()
    result = subprocess.run(
        [
            "docker", "run", "--rm",
            "--network=none",
            "--memory=128m",
            "--cpus=0.5",
            "--pids-limit=50",
            "-v", f"{WORKSPACE_DIR}:/workspace",  # only workspace, not full project
            "-w", "/workspace",                    # cwd inside container
            "python:3.12-slim",
            "bash", "-c", command
        ],
        capture_output=True,
        text=True,
        timeout=timeout + 5,
    )
    output = result.stdout.strip()
    error = result.stderr.strip()
    if error:
        return f"{output}\nSTDERR: {error}" if output else f"STDERR: {error}"
    return output or "(no output)"

def run_python_in_docker(code: str, timeout: int = 15) -> str:
    """Write Python code to a temp file and run it in Docker."""
    _ensure_workspace()
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "--network=none",
                "--memory=128m",
                "--cpus=0.5",
                "--pids-limit=50",
                "-v", f"{WORKSPACE_DIR}:/workspace",
                "-v", f"{tmp_path}:/code/script.py:ro",
                "-w", "/workspace",
                "python:3.12-slim",
                "python", "/code/script.py"
            ],
            capture_output=True,
            text=True,
            timeout=timeout + 5,
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        if error:
            return f"{output}\nSTDERR: {error}" if output else f"STDERR: {error}"
        return output or "(no output)"
    finally:
        os.unlink(tmp_path)

def run_restricted(command: str, timeout: int = 15) -> str:
    """Fallback: run in restricted subprocess, cwd set to workspace."""
    _ensure_workspace()
    if _is_dangerous(command):
        return "🚫 Blocked: command flagged as potentially dangerous."

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=WORKSPACE_DIR,  # restricted to workspace, not home dir
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        if error:
            return f"{output}\nSTDERR: {error}" if output else f"STDERR: {error}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return f"⏱ Timed out after {timeout}s"
    except Exception as e:
        return f"Error: {e}"


class Sandbox:
    def __init__(self, prefer_docker: bool = True, timeout: int = 15):
        self.timeout = timeout
        self.use_docker = prefer_docker and _docker_available()
        _ensure_workspace()
        if self.use_docker:
            print(f"  🐳 Sandbox: Docker — workspace only ({WORKSPACE_DIR})")
        else:
            print(f"  🔒 Sandbox: Restricted subprocess — workspace only ({WORKSPACE_DIR})")

    def run_bash(self, command: str) -> str:
        if self.use_docker:
            try:
                return run_in_docker(command, self.timeout)
            except subprocess.TimeoutExpired:
                return f"⏱ Timed out after {self.timeout}s"
            except Exception as e:
                return f"Docker error: {e}"
        else:
            return run_restricted(command, self.timeout)

    def run_python(self, code: str) -> str:
        if self.use_docker:
            try:
                return run_python_in_docker(code, self.timeout)
            except subprocess.TimeoutExpired:
                return f"⏱ Timed out after {self.timeout}s"
            except Exception as e:
                return f"Docker error: {e}"
        else:
            with tempfile.NamedTemporaryFile(
                mode='w', suffix='.py', delete=False
            ) as f:
                f.write(code)
                tmp_path = f.name
            try:
                return run_restricted(f"python3 {tmp_path}", self.timeout)
            finally:
                os.unlink(tmp_path)

    @property
    def mode(self) -> str:
        return "docker" if self.use_docker else "restricted"