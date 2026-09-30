from pathlib import Path

from scaffolding.steps.local_dependencies import LocalDependenciesStep


def test_local_dependencies_installs_backend_and_frontend_packages(tmp_path):
    (tmp_path / "apps" / "api").mkdir(parents=True)
    (tmp_path / "apps" / "web").mkdir(parents=True)
    calls = []

    def run(command, cwd=None, check=None):
        calls.append((command, Path(cwd), check))
        return None

    completed = LocalDependenciesStep(tmp_path, runner=run).execute()

    assert completed == [
        "python3 -m pip install -e .[dev]",
        "npm install",
    ]
    assert calls[0][1] == tmp_path / "apps" / "api"
    assert calls[1][1] == tmp_path / "apps" / "web"
    assert all(call[2] is True for call in calls)
