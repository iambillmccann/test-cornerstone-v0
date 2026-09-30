from app.core.config import Settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient


def _build_app_with_settings(settings: Settings) -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def _health() -> dict[str, str]:
        return {"status": "ok"}

    return app


def test_cors_allows_wildcard_pages_origin(monkeypatch):
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://*.cornerstone-9p8.pages.dev,http://localhost:5173",
    )
    settings = Settings()
    app = _build_app_with_settings(settings)
    client = TestClient(app)

    response = client.get(
        "/health",
        headers={"Origin": "https://a0eb8e9c.cornerstone-9p8.pages.dev"},
    )

    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin")
        == "https://a0eb8e9c.cornerstone-9p8.pages.dev"
    )


def test_cors_rejects_non_matching_wildcard_origin(monkeypatch):
    monkeypatch.setenv(
        "CORS_ORIGINS",
        "https://*.cornerstone-9p8.pages.dev,http://localhost:5173",
    )
    settings = Settings()
    app = _build_app_with_settings(settings)
    client = TestClient(app)

    response = client.get(
        "/health",
        headers={"Origin": "https://example.not-cornerstone.pages.dev"},
    )

    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") is None


def test_cors_origin_regex_extends_allowlist(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "http://localhost:5173")
    monkeypatch.setenv("CORS_ORIGIN_REGEX", r"^https://staging\.cornerstone\.com$")
    settings = Settings()
    app = _build_app_with_settings(settings)
    client = TestClient(app)

    response = client.get(
        "/health",
        headers={"Origin": "https://staging.cornerstone.com"},
    )

    assert response.status_code == 200
    assert (
        response.headers.get("access-control-allow-origin")
        == "https://staging.cornerstone.com"
    )
