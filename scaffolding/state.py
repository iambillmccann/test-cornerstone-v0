from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _sanitize_state(data: dict[str, Any]) -> dict[str, Any]:
    safe = dict(data)
    safe.pop("secrets", None)
    if "secrets" in safe:
        safe["secrets"] = {}
    if "completed_steps" not in safe:
        safe["completed_steps"] = []
    if "pending_steps" not in safe:
        safe["pending_steps"] = []
    safe["status"] = safe.get("status") or (
        "complete" if not safe.get("pending_steps") else "in_progress"
    )
    return safe


def save_state(path: str | Path, state: dict[str, Any] | Any) -> dict[str, Any]:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    payload = state if isinstance(state, dict) else state.__dict__
    cleaned = _sanitize_state(payload)
    cleaned["secrets"] = {}
    target.write_text(
        json.dumps(cleaned, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return cleaned


def load_state(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        return {
            "version": 1,
            "completed_steps": [],
            "pending_steps": [],
            "status": "new",
            "secrets": {},
        }

    payload = json.loads(target.read_text(encoding="utf-8"))
    payload["secrets"] = {}
    if not payload.get("completed_steps"):
        payload["completed_steps"] = []
    if not payload.get("pending_steps"):
        payload["pending_steps"] = []
    payload["status"] = payload.get("status") or (
        "complete" if not payload.get("pending_steps") else "in_progress"
    )
    return payload


class ScaffoldState(dict):
    def __init__(
        self,
        version: int = 1,
        application: dict[str, Any] | None = None,
        provider: str = "aws",
        region: str = "us-east-1",
        completed_steps: list[str] | None = None,
        pending_steps: list[str] | None = None,
        secrets: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            version=version,
            application=application or {"name": "Cornerstone", "slug": "cornerstone"},
            provider=provider,
            region=region,
            completed_steps=completed_steps or [],
            pending_steps=pending_steps or [],
            secrets={},
            **kwargs,
        )
        if secrets:
            self["secrets"] = {}
        self["status"] = self.get("status") or (
            "complete" if not self.get("pending_steps") else "in_progress"
        )

    def __getattr__(self, item: str) -> Any:
        return self[item]
