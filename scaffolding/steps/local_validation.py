from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable

CommandRunner = Callable[..., subprocess.CompletedProcess]


class LocalValidationStep:
    """Validate the generated local environment without starting long-lived servers."""

    def __init__(self, repo_root: str | Path, runner: CommandRunner | None = None):
        self.repo_root = Path(repo_root)
        self.runner = runner or subprocess.run

    def execute(self) -> list[str]:
        self._require_files()
        commands = [
            (["alembic", "upgrade", "head"], self.repo_root / "apps" / "api"),
            (["pytest"], self.repo_root / "apps" / "api"),
            (["npm", "run", "build"], self.repo_root / "apps" / "web"),
        ]
        completed: list[str] = []
        for command, cwd in commands:
            self.runner(command, cwd=cwd, check=True)
            completed.append(" ".join(command))
        return completed

    def _require_files(self) -> None:
        required_files = (
            self.repo_root / ".env.local",
            self.repo_root / "apps" / "api" / ".env",
            self.repo_root / "apps" / "web" / ".env.local",
        )
        missing = [
            str(path.relative_to(self.repo_root))
            for path in required_files
            if not path.exists()
        ]
        if missing:
            raise RuntimeError(
                f"Local environment is incomplete; missing: {', '.join(missing)}"
            )
