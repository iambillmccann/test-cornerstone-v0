from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scaffolding.state import load_state

DEFAULT_PHASES = [
    "configure",
    "specialize",
    "local_environment",
    "local_dependencies",
    "local_database",
    "local_validation",
    "authentication",
    "cloud_bootstrap",
    "cloud_provision",
    "cloud_deploy",
    "validation",
    "finalize",
]


def detect_state(repo_root: str | Path) -> dict[str, Any] | None:
    root = Path(repo_root)
    state_path = root / ".cornerstone" / "state.json"
    if not state_path.exists():
        return None
    return load_state(state_path)


def next_pending_step(state: dict[str, Any]) -> str | None:
    pending = list(state.get("pending_steps") or [])
    if pending:
        return pending[0]
    return None


def phase_status(state: dict[str, Any]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    completed = set(state.get("completed_steps") or [])
    pending = set(state.get("pending_steps") or [])
    for phase in DEFAULT_PHASES:
        if phase in completed:
            statuses[phase] = "complete"
        elif phase in pending:
            statuses[phase] = "pending"
        else:
            statuses[phase] = "not_started"
    return statuses


def load_or_init_state(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    state = detect_state(root)
    if state is not None:
        return state

    state_path = root / ".cornerstone" / "state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    initial_state = {
        "version": 1,
        "application": {"name": "Cornerstone", "slug": "cornerstone"},
        "provider": "aws",
        "region": "us-east-1",
        "completed_steps": [],
        "pending_steps": list(DEFAULT_PHASES),
        "status": "in_progress",
        "secrets": {},
    }
    state_path.write_text(
        json.dumps(initial_state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return initial_state


def save_state(repo_root: str | Path, state: dict[str, Any]) -> dict[str, Any]:
    state_path = Path(repo_root) / ".cornerstone" / "state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return state


def complete_step(state: dict[str, Any], step: str) -> dict[str, Any]:
    completed = list(state.get("completed_steps") or [])
    pending = list(state.get("pending_steps") or [])
    if step not in completed:
        completed.append(step)
    if step in pending:
        pending.remove(step)
    state["completed_steps"] = completed
    state["pending_steps"] = pending
    state["status"] = "complete" if not pending else "in_progress"
    return state
