# layer_07/orchestrator.py
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from layer_07.sub_agent import SubAgent

# Pre-defined specialist sub-agents
SPECIALISTS = {
    "researcher": {
        "goal": "Research and gather information by reading files, running commands, and exploring the codebase.",
        "description": "Researches and gathers information from files and the system",
    },
    "coder": {
        "goal": "Write clean, working code and save it to files.",
        "description": "Writes code and saves it to files",
    },
    "reviewer": {
        "goal": "Review code or output for correctness, bugs, and improvements.",
        "description": "Reviews code or content and provides feedback",
    },
    "executor": {
        "goal": "Execute shell commands and return their output.",
        "description": "Runs shell commands and reports results",
    },
    "tester": {
        "goal": "Write and run unit tests for code, report pass/fail results.",
        "description": "Writes and executes tests for code",
    },
}

class Orchestrator:
    """
    Manages and runs sub-agents. Can be called as a tool by the main agent.
    """
    def __init__(self, model: str | None = None):
        self.model = model
        self.results: dict[str, str] = {}

    def run_agent(self, agent_type: str, task: str) -> str:
        """Spawn a sub-agent of the given type and run it on a task."""
        if agent_type not in SPECIALISTS:
            available = ", ".join(SPECIALISTS.keys())
            return f"Unknown agent type '{agent_type}'. Available: {available}"

        spec = SPECIALISTS[agent_type]
        agent = SubAgent(
            name=agent_type,
            goal=spec["goal"],
            model=self.model,
        )
        result = agent.run(task)
        self.results[agent_type] = result
        return result

    def run_parallel(self, tasks: list[dict]) -> dict[str, str]:
        """
        Run multiple sub-agents. Each task is {"agent": "coder", "task": "..."}.
        Note: runs sequentially for now (parallel in Layer 8+).
        """
        results = {}
        for t in tasks:
            agent_type = t.get("agent", "executor")
            task = t.get("task", "")
            results[agent_type] = self.run_agent(agent_type, task)
        return results

    def tools(self) -> list:
        """Return tool schemas so the main agent can call sub-agents."""
        from layer_02.tools import Tool

        agent_descriptions = "\n".join(
            f"  - {k}: {v['description']}"
            for k, v in SPECIALISTS.items()
        )

        return [
            Tool(
                name="spawn_agent",
                description=(
                    f"Spawn a specialist sub-agent to handle a focused task.\n"
                    f"Available agent types:\n{agent_descriptions}"
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "agent_type": {
                            "type": "string",
                            "enum": list(SPECIALISTS.keys()),
                            "description": "The type of specialist agent to spawn"
                        },
                        "task": {
                            "type": "string",
                            "description": "Clear, specific task description for the agent"
                        }
                    },
                    "required": ["agent_type", "task"]
                },
                fn=lambda agent_type, task: self.run_agent(agent_type, task)
            )
        ]