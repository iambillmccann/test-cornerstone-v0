This document contains references to Cornerstone

# Cornerstone API

FastAPI backend for the Cornerstone project.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

Start local PostgreSQL from repo root:

```bash
./scripts/dev-db-up.sh
```

## Endpoints

### Health & Status

- `GET /api/v1/health` — Health check
- `GET /api/v1/ready` — Readiness check
- `GET /api/v1/version` — API version info

### Authentication (Clerk-based)

- `GET /api/me` (canonical) — Returns authenticated app user profile (requires `Authorization: Bearer <clerk_token>`)
  - Response: `{ id, email, display_name, avatar_url }`
  - Bootstraps local user on first call; idempotent thereafter
- `GET /api/v1/auth/me` (legacy) — Returns verified Clerk token identity claims (for debugging)

## Testing

Install dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=html
```

## Migrations

Run migrations from `apps/api`:

```bash
alembic upgrade head
```

Reset migration state for reproducibility checks:

```bash
alembic downgrade base
alembic upgrade head
```

## Configuration

Create environment variables from the repo root `.env.example` and ensure `DATABASE_URL` points to the local PostgreSQL container:

`postgresql+psycopg://postgres:postgres@localhost:5432/cornerstone`

Auth-related settings:

- `CLERK_JWKS_URL`: required for Clerk JWT signature verification
- `CLERK_ISSUER`: optional strict issuer check
- `CLERK_AUDIENCE`: optional strict audience check

Database-related setting:

- `DATABASE_URL`: SQLAlchemy connection URL used by runtime and Alembic

CORS-related settings:

- `CORS_ORIGINS`: comma-separated allowlist of exact origins. Supports wildcard entries such as `https://*.your-project.pages.dev` for preview deployments.
- `CORS_ORIGIN_REGEX`: optional advanced regex appended to the computed allow-origin regex.
