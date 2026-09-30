import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parents[2]


def run_cli(repo_root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    return subprocess.run(
        [sys.executable, "-m", "scaffolding.cli", *args],
        cwd=repo_root,
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )


def test_help_describes_cli_commands_without_creating_state(tmp_path):
    result = run_cli(tmp_path, "--repo-root", str(tmp_path), "--help")

    assert result.returncode == 0
    assert "Cornerstone application setup" in result.stdout
    assert "status" in result.stdout
    assert "run" in result.stdout
    assert not (tmp_path / ".cornerstone" / "state.json").exists()


def test_status_reports_uninitialized_repository_without_creating_state(tmp_path):
    result = run_cli(tmp_path, "status")

    assert result.returncode == 0
    assert "Not initialized" in result.stdout
    assert not (tmp_path / ".cornerstone" / "state.json").exists()


def test_run_initializes_state_and_reports_next_step(tmp_path):
    result = run_cli(tmp_path, "run", "--plan")

    assert result.returncode == 0
    assert "Starting Cornerstone application setup" in result.stdout
    assert "configure" in result.stdout

    state = json.loads(
        (tmp_path / ".cornerstone" / "state.json").read_text(encoding="utf-8")
    )
    assert state["status"] == "in_progress"
    assert state["pending_steps"][0] == "configure"


def test_no_command_starts_setup_like_the_root_invocation(tmp_path):
    result = run_cli(tmp_path, "--repo-root", str(tmp_path), "run", "--plan")

    assert result.returncode == 0
    assert "Starting Cornerstone application setup" in result.stdout
