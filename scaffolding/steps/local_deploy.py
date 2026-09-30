from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


class LocalDeployStep:
    """Orchestrate local app setup and validation for the AWS-first lifecycle."""

    def __init__(self, repo_root: str | Path):
        self.repo_root = Path(repo_root)

    @property
    def state_path(self) -> Path:
        return self.repo_root / ".cornerstone" / "state.json"

    def status(self) -> bool:
        state = self._read_state()
        return "local_environment" in (state.get("completed_steps") or [])

    def _read_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {
                "completed_steps": [],
                "pending_steps": [
                    "configure",
                    "specialize",
                    "local_environment",
                    "local_database",
                ],
                "status": "in_progress",
            }
        return json.loads(self.state_path.read_text(encoding="utf-8"))

    def execute(self) -> dict[str, Any]:
        env = os.environ.copy()
        env.setdefault("POSTGRES_USER", "postgres")
        env.setdefault("POSTGRES_PASSWORD", "postgres")
        env.setdefault("POSTGRES_DB", "cornerstone")
        env.setdefault("POSTGRES_HOST", "localhost")
        env.setdefault("POSTGRES_PORT", "5432")

        subprocess.run(
            ["docker", "compose", "up", "-d", "db"],
            cwd=self.repo_root,
            env=env,
            check=True,
        )

        state = self._read_state()
        completed = list(state.get("completed_steps") or [])
        if "local_environment" not in completed:
            completed.append("local_environment")
        if "local_database" not in completed:
            completed.append("local_database")
        state["completed_steps"] = completed
        state["status"] = "in_progress"
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        return state

    def rollback(self) -> None:
        subprocess.run(["docker", "compose", "down"], cwd=self.repo_root, check=False)
