import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parents[2]


def test_run_preserves_failed_step_when_external_command_fails(tmp_path):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)
    result = subprocess.run(
        [sys.executable, "-m", "scaffolding.cli", "run"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Progress was preserved" in result.stdout
    state = json.loads(
        (tmp_path / ".cornerstone" / "state.json").read_text(encoding="utf-8")
    )
    assert state["status"] == "failed"
    assert state["failed_step"] == "local_dependencies"
