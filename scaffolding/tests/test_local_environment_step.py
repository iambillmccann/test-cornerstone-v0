from scaffolding.config import ApplicationConfig
from scaffolding.steps.local_environment import LocalEnvironmentStep


def test_local_environment_step_generates_root_and_app_env_files(tmp_path):
    repo_root = tmp_path / "repo"
    (repo_root / "apps" / "api").mkdir(parents=True)
    (repo_root / "apps" / "web").mkdir(parents=True)

    config = ApplicationConfig()
    config.application.display_name = "ReviewLens AI"
    config.application.slug = "reviewlens-ai"
    config.application.api_name = "reviewlens-ai-api"
    config.application.version = "0.1.0"
    config.local.database_name = "reviewlens_ai"

    step = LocalEnvironmentStep(repo_root, config)
    step.execute()

    root_env = (repo_root / ".env.local").read_text(encoding="utf-8")
    api_env = (repo_root / "apps" / "api" / ".env").read_text(encoding="utf-8")
    web_env = (repo_root / "apps" / "web" / ".env.local").read_text(encoding="utf-8")

    assert "APP_DISPLAY_NAME=ReviewLens AI" in root_env
    assert "APP_SLUG=reviewlens-ai" in root_env
    assert "POSTGRES_DB=reviewlens_ai" in root_env
    assert (
        "DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/reviewlens_ai"
        in root_env
    )
    assert "APP_NAME=reviewlens-ai-api" in api_env
    assert "DATABASE_NAME=reviewlens_ai" in api_env
    assert "VITE_APP_SLUG=reviewlens-ai" in web_env
    assert "VITE_CLERK_PUBLISHABLE_KEY=" in web_env


def test_local_environment_step_preserves_existing_auth_values(tmp_path):
    (tmp_path / "apps" / "api").mkdir(parents=True)
    (tmp_path / "apps" / "web").mkdir(parents=True)
    (tmp_path / ".env.local").write_text("CLERK_SECRET_KEY=keep-me\n", encoding="utf-8")
    (tmp_path / "apps" / "web" / ".env.local").write_text(
        "VITE_CLERK_PUBLISHABLE_KEY=pk_test_existing\n", encoding="utf-8"
    )

    LocalEnvironmentStep(tmp_path, ApplicationConfig()).execute()

    assert "CLERK_SECRET_KEY=keep-me" in (tmp_path / ".env.local").read_text()
    assert (
        "VITE_CLERK_PUBLISHABLE_KEY=pk_test_existing"
        in (tmp_path / "apps" / "web" / ".env.local").read_text()
    )
