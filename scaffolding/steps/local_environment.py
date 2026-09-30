from __future__ import annotations

from pathlib import Path

from scaffolding.config import ApplicationConfig


class LocalEnvironmentStep:
    """Generate local app-specific environment files for development."""

    def __init__(self, repo_root: str | Path, config: ApplicationConfig):
        self.repo_root = Path(repo_root)
        self.config = config

    def status(self) -> bool:
        return (
            (self.repo_root / ".env.local").exists()
            and (self.repo_root / "apps" / "api" / ".env").exists()
            and (self.repo_root / "apps" / "web" / ".env.local").exists()
        )

    def execute(self) -> dict[str, str]:
        root_env = self._root_env_contents()
        api_env = self._api_env_contents()
        web_env = self._web_env_contents()

        self._write_preserving_values(self.repo_root / ".env.local", root_env)
        self._write_preserving_values(self.repo_root / "apps" / "api" / ".env", api_env)
        self._write_preserving_values(
            self.repo_root / "apps" / "web" / ".env.local", web_env
        )

        return {
            "root": root_env,
            "api": api_env,
            "web": web_env,
        }

    def _write_preserving_values(self, path: Path, generated: str) -> None:
        existing = self._read_values(path)
        lines = []
        for line in generated.splitlines():
            key, separator, value = line.partition("=")
            if separator and not value and key in existing:
                line = f"{key}={existing[key]}"
            lines.append(line)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    @staticmethod
    def _read_values(path: Path) -> dict[str, str]:
        if not path.exists():
            return {}
        values: dict[str, str] = {}
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                values[key.strip()] = value
        return values

    def _root_env_contents(self) -> str:
        lines = [
            "# Application",
            f"APP_NAME={self.config.application.slug}",
            f"APP_DISPLAY_NAME={self.config.application.display_name}",
            f"APP_SLUG={self.config.application.slug}",
            "APP_ENV=local",
            "",
            "# API",
            f"API_NAME={self.config.application.api_name}",
            "API_HOST=localhost",
            "API_PORT=8000",
            "",
            "# Web",
            "WEB_HOST=localhost",
            "WEB_PORT=5173",
            "VITE_CLERK_PUBLISHABLE_KEY=",
            "VITE_API_BASE_URL=http://localhost:8000",
            "",
            "# Database",
            "POSTGRES_USER=postgres",
            "POSTGRES_PASSWORD=postgres",
            f"POSTGRES_DB={self.config.local.database_name}",
            "POSTGRES_HOST=localhost",
            "POSTGRES_PORT=5432",
            f"DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/{self.config.local.database_name}",
            "",
            "# Clerk",
            "CLERK_PUBLISHABLE_KEY=",
            "CLERK_SECRET_KEY=",
            "CLERK_JWKS_URL=",
            "CLERK_ISSUER=",
            "CLERK_AUDIENCE=",
            "",
            "# AWS / CI defaults for template portability",
            "AWS_PROFILE=cornerstone",
            "GITHUB_OWNER=fourier-gauss-labs",
            "GITHUB_REPO=cornerstone",
            "AWS_ROLE_NAME=github-actions-cornerstone-deploy",
            "",
            "# Observability",
            "SENTRY_DSN=",
        ]
        return "\n".join(lines) + "\n"

    def _api_env_contents(self) -> str:
        lines = [
            "# API Configuration",
            f"APP_NAME={self.config.application.api_name}",
            f"APP_SLUG={self.config.application.slug}",
            f"API_NAME={self.config.application.api_name}",
            f"APP_VERSION={self.config.application.version}",
            f"DATABASE_NAME={self.config.local.database_name}",
            "",
            "# Clerk token verification (backend)",
            "CLERK_JWKS_URL=",
            "CLERK_ISSUER=",
            "CLERK_AUDIENCE=",
            "",
            "# CORS Origins (comma-separated)",
            "CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173,http://127.0.0.1:4173,http://localhost:4174,http://127.0.0.1:4174,http://localhost:3000,http://127.0.0.1:3000",
            "# Optional extra regex (advanced): append to the computed allow-origin regex",
            "# CORS_ORIGIN_REGEX=",
            "",
            "# Optional: explicit database URL override for migrations/runtime",
            f"DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/{self.config.local.database_name}",
        ]
        return "\n".join(lines) + "\n"

    def _web_env_contents(self) -> str:
        lines = [
            f"VITE_APP_SLUG={self.config.application.slug}",
            f"VITE_APP_DISPLAY_NAME={self.config.application.display_name}",
            f"VITE_APP_DESCRIPTION={self.config.application.display_name} SaaS app",
            f"VITE_API_NAME={self.config.application.api_name}",
            "VITE_CLERK_PUBLISHABLE_KEY=",
            "VITE_API_BASE_URL=http://localhost:8000",
        ]
        return "\n".join(lines) + "\n"
