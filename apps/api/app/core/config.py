import os
import re
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict


def _load_local_env_files() -> None:
    """Load local env files into process env for development ergonomics."""
    config_path = Path(__file__).resolve()
    api_root = config_path.parents[2]
    repo_root = next(
        (
            parent
            for parent in [api_root, *api_root.parents]
            if (parent / ".git").exists() or (parent / "docker-compose.yml").exists()
        ),
        api_root,
    )

    env_files = [
        api_root / ".env",
        repo_root / ".env.local",
    ]

    for env_file in env_files:
        if not env_file.exists():
            continue

        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            # Keep explicitly exported shell env vars authoritative.
            os.environ.setdefault(key.strip(), value.strip())


_load_local_env_files()


LOCALHOST_ORIGIN_REGEX = r"https?://(localhost|127\.0\.0\.1)(:\d+)?"
DEFAULT_APP_SLUG = os.getenv("APP_SLUG", "cornerstone")
DEFAULT_API_NAME = os.getenv("API_NAME", "cornerstone-api")
DEFAULT_API_VERSION = os.getenv("API_VERSION", "0.1.0")
DEFAULT_DATABASE_NAME = os.getenv("DATABASE_NAME", DEFAULT_APP_SLUG)


def _wildcard_origin_to_regex(origin: str) -> str:
    """Convert a wildcard origin like https://*.example.com to a full-match regex."""
    escaped = re.escape(origin)
    wildcard_regex = escaped.replace(r"\*", r"[^.]+")
    return f"^{wildcard_regex}$"


def _combine_regexes(regexes: list[str]) -> str | None:
    parts = [part.strip() for part in regexes if part and part.strip()]
    if not parts:
        return None
    return "|".join(f"(?:{part})" for part in parts)


def _parse_cors_origins(raw: str) -> tuple[list[str], list[str]]:
    exact_origins: list[str] = []
    wildcard_regexes: list[str] = []

    for entry in raw.split(","):
        origin = entry.strip()
        if not origin:
            continue

        if "*" in origin:
            wildcard_regexes.append(_wildcard_origin_to_regex(origin))
            continue

        exact_origins.append(origin)

    return exact_origins, wildcard_regexes


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = DEFAULT_API_NAME
    app_version: str = DEFAULT_API_VERSION
    database_url: str = (
        f"postgresql+psycopg://postgres:postgres@localhost:5432/{DEFAULT_DATABASE_NAME}"
    )
    clerk_jwks_url: str | None = None
    clerk_issuer: str | None = None
    clerk_audience: str | None = None
    clerk_secret_key: str | None = None
    cors_origin_regex: str | None = LOCALHOST_ORIGIN_REGEX
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:4174",
        "http://127.0.0.1:4174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    def __init__(self, **data):
        super().__init__(**data)

        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            parsed_origins, wildcard_regexes = _parse_cors_origins(cors_env)
            self.cors_origins = parsed_origins
            self.cors_origin_regex = _combine_regexes(
                [LOCALHOST_ORIGIN_REGEX, *wildcard_regexes]
            )

        cors_regex_env = os.getenv("CORS_ORIGIN_REGEX")
        if cors_regex_env:
            self.cors_origin_regex = _combine_regexes(
                [self.cors_origin_regex or "", cors_regex_env]
            )

        self.database_url = os.getenv("DATABASE_URL", self.database_url)
        self.clerk_jwks_url = os.getenv("CLERK_JWKS_URL", self.clerk_jwks_url)
        self.clerk_issuer = os.getenv("CLERK_ISSUER", self.clerk_issuer)
        self.clerk_audience = os.getenv("CLERK_AUDIENCE", self.clerk_audience)
        self.clerk_secret_key = os.getenv("CLERK_SECRET_KEY", self.clerk_secret_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
