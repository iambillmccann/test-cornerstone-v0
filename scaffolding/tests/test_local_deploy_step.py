import json
from pathlib import Path

from scaffolding.steps.local_deploy import LocalDeployStep


def test_local_deploy_step_marks_local_setup_complete(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".cornerstone").mkdir()
    state_path = repo_root / ".cornerstone" / "state.json"
    state_path.write_text(
        json.dumps(
            {
                "version": 1,
                "completed_steps": ["configure", "specialize"],
                "pending_steps": ["local_environment", "local_database"],
                "status": "in_progress",
            }
        ),
        encoding="utf-8",
    )

    commands = []

    def fake_run(args, cwd=None, env=None, check=None):
        commands.append({"args": args, "cwd": str(cwd), "env": env, "check": check})
        return None

    monkeypatch.setattr("subprocess.run", fake_run)

    step = LocalDeployStep(repo_root)
    result = step.execute()

    assert "local_environment" in result["completed_steps"]
    assert "local_database" in result["completed_steps"]
    assert commands[0]["args"][:3] == ["docker", "compose", "up"]


def test_local_deploy_step_rollback_runs_compose_down(tmp_path, monkeypatch):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    calls = []

    def fake_run(args, cwd=None, check=None):
        calls.append({"args": args, "cwd": str(cwd), "check": check})
        return None

    monkeypatch.setattr("subprocess.run", fake_run)

    step = LocalDeployStep(repo_root)
    step.rollback()

    assert calls[0]["args"][:2] == ["docker", "compose"]
    assert calls[0]["args"][-1] == "down"
