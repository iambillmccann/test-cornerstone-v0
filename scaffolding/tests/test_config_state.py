from pathlib import Path

from scaffolding.config import ApplicationConfig
from scaffolding.state import ScaffoldState, load_state, save_state


def test_application_config_uses_default_identity_values():
    config = ApplicationConfig()

    assert config.application.display_name == "Cornerstone"
    assert config.application.slug == "cornerstone"
    assert config.application.api_name == "cornerstone-api"
    assert config.application.version == "0.1.0"
    assert config.local.database_name == "cornerstone"


def test_application_config_derives_repository_defaults_from_git_context(tmp_path):
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    (repo_root / ".git").mkdir()

    config = ApplicationConfig.from_repository_root(repo_root)

    assert config.repository.owner == "local"
    assert config.repository.name == "repo"
    assert config.cloud.provider == "aws"
    assert config.cloud.region == "us-east-1"


def test_state_persistence_redacts_secrets(tmp_path):
    repo_root = tmp_path / "repo"
    state_path = repo_root / ".cornerstone" / "state.json"
    state_path.parent.mkdir(parents=True)

    state = ScaffoldState(
        version=1,
        application={"name": "ReviewLens AI", "slug": "reviewlens-ai"},
        provider="aws",
        region="us-east-1",
        completed_steps=["configure", "specialize"],
        pending_steps=["authentication"],
        secrets={"clerk_secret_key": "super-secret", "github_token": "token"},
    )

    save_state(state_path, state)
    persisted = load_state(state_path)

    assert persisted["application"]["name"] == "ReviewLens AI"
    assert persisted["secrets"] == {}
    assert "super-secret" not in str(persisted)
    assert "token" not in str(persisted)


def test_state_step_progress_supports_resume_tracking(tmp_path):
    repo_root = tmp_path / "repo"
    state_path = repo_root / ".cornerstone" / "state.json"
    state_path.parent.mkdir(parents=True)

    state = ScaffoldState(
        version=1,
        application={"name": "ReviewLens AI", "slug": "reviewlens-ai"},
        provider="aws",
        region="us-east-1",
        completed_steps=["configure", "specialize"],
        pending_steps=["authentication", "cloud_bootstrap"],
    )

    save_state(state_path, state)
    reloaded = load_state(state_path)

    assert reloaded["completed_steps"] == ["configure", "specialize"]
    assert reloaded["pending_steps"] == ["authentication", "cloud_bootstrap"]
    assert reloaded["status"] == "in_progress"
