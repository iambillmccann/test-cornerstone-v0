from pathlib import Path

from scaffolding.steps.local_validation import LocalValidationStep


def test_local_validation_runs_migrations_tests_and_frontend_build(tmp_path):
    (tmp_path / ".env.local").write_text("", encoding="utf-8")
    (tmp_path / "apps" / "api").mkdir(parents=True)
    (tmp_path / "apps" / "web").mkdir(parents=True)
    (tmp_path / "apps" / "api" / ".env").write_text("", encoding="utf-8")
    (tmp_path / "apps" / "web" / ".env.local").write_text("", encoding="utf-8")
    calls = []

    def run(command, cwd=None, check=None):
        calls.append((command, Path(cwd), check))
        return None

    completed = LocalValidationStep(tmp_path, runner=run).execute()

    assert completed == [
        "alembic upgrade head",
        "pytest",
        "npm run build",
    ]
    assert calls[0][1] == tmp_path / "apps" / "api"
    assert calls[2][1] == tmp_path / "apps" / "web"
    assert all(call[2] is True for call in calls)


def test_local_validation_reports_missing_environment_files(tmp_path):
    try:
        LocalValidationStep(tmp_path, runner=lambda *_args, **_kwargs: None).execute()
    except RuntimeError as exc:
        assert "Local environment is incomplete" in str(exc)
        assert ".env.local" in str(exc)
    else:
        raise AssertionError("expected incomplete local environment failure")
