from pathlib import Path

from scaffolding.runner import detect_state, next_pending_step
from scaffolding.state import save_state


def test_detect_state_reads_existing_resume_file(tmp_path):
    repo_root = tmp_path / "app"
    state_path = repo_root / ".cornerstone" / "state.json"
    state_path.parent.mkdir(parents=True)
    save_state(
        state_path,
        {
            "version": 1,
            "application": {"name": "ReviewLens AI", "slug": "reviewlens-ai"},
            "provider": "aws",
            "region": "us-east-1",
            "completed_steps": ["configure", "specialize"],
            "pending_steps": ["authentication", "cloud_bootstrap"],
        },
    )

    state = detect_state(repo_root)

    assert state is not None
    assert state["provider"] == "aws"
    assert state["application"]["slug"] == "reviewlens-ai"


def test_next_pending_step_returns_first_resume_target():
    state = {
        "completed_steps": ["configure", "specialize"],
        "pending_steps": ["authentication", "cloud_bootstrap"],
    }

    assert next_pending_step(state) == "authentication"

    empty_state = {"completed_steps": ["configure"], "pending_steps": []}
    assert next_pending_step(empty_state) is None
