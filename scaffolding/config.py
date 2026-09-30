from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ApplicationIdentity:
    display_name: str = "Cornerstone"
    slug: str = "cornerstone"
    api_name: str = "cornerstone-api"
    version: str = "0.1.0"


@dataclass
class RepositoryIdentity:
    owner: str = "local"
    name: str = "repo"


@dataclass
class LocalSettings:
    database_name: str = "cornerstone"


@dataclass
class CloudSettings:
    provider: str = "aws"
    region: str = "us-east-1"


@dataclass
class ApplicationConfig:
    application: ApplicationIdentity = field(default_factory=ApplicationIdentity)
    repository: RepositoryIdentity = field(default_factory=RepositoryIdentity)
    local: LocalSettings = field(default_factory=LocalSettings)
    cloud: CloudSettings = field(default_factory=CloudSettings)

    @classmethod
    def from_repository_root(cls, repo_root: Path | str) -> "ApplicationConfig":
        root = Path(repo_root)
        repo_name = root.name or "repo"
        defaults = cls()
        defaults.repository.name = repo_name
        defaults.repository.owner = "local"
        scaffold_path = root / "scaffold.env"
        if scaffold_path.exists():
            values = {}
            for raw_line in scaffold_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    values[key.strip()] = value.strip().strip('"')
            defaults.application.display_name = values.get(
                "APP_DISPLAY_NAME", defaults.application.display_name
            )
            defaults.application.slug = values.get(
                "APP_SLUG", defaults.application.slug
            )
            defaults.application.api_name = values.get(
                "API_NAME", defaults.application.api_name
            )
            defaults.application.version = values.get(
                "API_VERSION", defaults.application.version
            )
            defaults.local.database_name = values.get(
                "DATABASE_NAME", defaults.application.slug.replace("-", "_")
            )
            defaults.repository.owner = values.get("GITHUB_OWNER", "local")
            defaults.repository.name = values.get("GITHUB_REPO", repo_name)
        return defaults

    def as_dict(self) -> dict:
        return {
            "application": {
                "display_name": self.application.display_name,
                "slug": self.application.slug,
                "api_name": self.application.api_name,
                "version": self.application.version,
            },
            "repository": {
                "owner": self.repository.owner,
                "name": self.repository.name,
            },
            "local": {
                "database_name": self.local.database_name,
            },
            "cloud": {
                "provider": self.cloud.provider,
                "region": self.cloud.region,
            },
        }
