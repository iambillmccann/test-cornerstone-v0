from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable

CommandRunner = Callable[..., subprocess.CompletedProcess]


class LocalDependenciesStep:
    """Install backend and frontend dependencies for local development."""

    def __init__(self, repo_root: str | Path, runner: CommandRunner | None = None):
        self.repo_root = Path(repo_root)
        self.runner = runner or subprocess.run

    def execute(self) -> list[str]:
        commands = [
            (
                ["python3", "-m", "pip", "install", "-e", ".[dev]"],
                self.repo_root / "apps" / "api",
            ),
            (["npm", "install"], self.repo_root / "apps" / "web"),
        ]
        completed: list[str] = []
        for command, cwd in commands:
            self.runner(command, cwd=cwd, check=True)
            completed.append(" ".join(command))
        return completed
