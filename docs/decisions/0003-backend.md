This document contains references to Cornerstone

# 0003: Backend Operational Architecture and CI Baseline

## Status

Accepted - 2026-05-12

## Context

After frontend scaffold decisions were established, backend implementation introduced several foundational patterns across auth, persistence, routing, and configuration. These choices were captured in development logs and code but were not formalized in the decisions catalog.

At the same time, repository CI only validated directory structure and did not enforce web/api quality gates on every push.

## Decision A: Clerk JWT Verification in API Runtime

Cornerstone verifies Clerk bearer tokens in API runtime using JWKS and `PyJWT` instead of delegating request-path token verification to a Clerk SDK.

Details:

- Fetch JWKS from configured `CLERK_JWKS_URL`.
- Resolve signing key by `kid`.
- Verify RS256 signature locally.
- Apply optional strict checks via `CLERK_ISSUER` and `CLERK_AUDIENCE`.

Rationale:

- Keeps request-path verification explicit and framework-native.
- Avoids adding another auth abstraction in core API flow.

## Decision B: Hybrid API Route Strategy

Cornerstone uses a hybrid route strategy:

- Canonical app-shell identity endpoint: `/api/me` (unversioned).
- Versioned resource and diagnostic endpoints remain under `/api/v1/*`.

Rationale:

- Stabilizes frontend bootstrap contract.
- Preserves versioned API evolution for broader endpoint surface.

## Decision C: Lazy Local User Provisioning

On first authenticated request, backend lazily creates or resolves local user state via `get_or_create_local_user_with_default_workspace`.

Rationale:

- Avoids webhook dependency for initial local identity creation.
- Ensures idempotent user/workspace bootstrap from authentication flow.

## Decision D: Centralized Environment Configuration

Backend runtime configuration is centralized in `app/core/config.py`, including environment loading and explicit overrides for auth/database settings.

Rationale:

- Single source of truth for runtime settings.
- Consistent behavior across API runtime and migration workflows.

## Decision E: Clerk Profile API Header Requirement

Profile enrichment calls to Clerk management API must include `User-Agent` and `Accept` headers.

Rationale:

- Prevents Cloudflare bot/WAF rejection observed when urllib default headers are used.
- Makes external profile hydration reliable in operational environments.

## Decision F: CI Baseline for Monorepo Verification

CI verifies both applications on every push and pull request using separate jobs with path-aware filtering:

- `web-checks`: lint, typecheck, build (runs only when `apps/web/**` or CI workflow changes).
- `api-checks`: lint (Ruff), tests (pytest) (runs only when `apps/api/**` or CI workflow changes).
- Both checks always run on pull requests regardless of changed files (safe default).

Runtime selections:

- Node `20.19.0` for web checks.
- Python `3.12` for API checks.
- GitHub Actions majors pinned to Node 24-based releases: `actions/checkout@v6`, `actions/setup-node@v6`, `actions/setup-python@v6`.

Path filtering strategy:

- Uses `dorny/paths-filter@v1` to detect which parts of the monorepo changed.
- Documentation-only commits skip both checks entirely.
- Reduces CI noise and resource usage for non-code changes.

Rationale:

- Delivers immediate feedback for both app surfaces without unnecessary overhead.
- Prevents drift by enforcing repeatable quality gates in shared workflow.
- Monorepo-aware filtering lets developers iterate faster on single-app changes.
- Avoids the pending Node 20 runtime deprecation on GitHub-hosted actions.

## Decision G: Railway Deployment & PostgreSQL

Backend and database are deployed on Railway with the following operational decisions:

- **Container runtime**: Python 3.12 (pinned via `.python-version` file to match local development environment).
- **API build**: Editable install via `pip install -e .` during build; reinstalled at startup to ensure runtime layer has all packages.
- **Start command**: `python -m pip install -e . && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Database**: Railway PostgreSQL with persistent volume (`postgres-volume`).
- **Configuration robustness**: App config uses depth-agnostic repo root detection (`.git` or `docker-compose.yml` marker) instead of hardcoded path indexing.
- **Migration workflow**: Alembic migrations executed via Railway CLI using public DB endpoint (internal `postgres.railway.internal` host not accessible from local machine).

Rationale:

- Railway managed infrastructure reduces operational burden.
- Python version pinning across local/Railway prevents runtime surprises.
- Startup pip reinstall ensures build/runtime layer coherence in Railway's nixpacks builder.
- Config robustness makes deployment portable across different directory layouts.
- Public DB endpoint enables migration tooling from local CLI while keeping API runtime isolated on private network.

## Decision H: CORS Wildcard Origin Support (2026-05-14)

Cornerstone backend now supports wildcard CORS origins (e.g. `https://*.your-project.pages.dev`) via the `CORS_ORIGINS` environment variable, enabling seamless integration with Cloudflare Pages preview deployments and similar ephemeral frontend URLs.

Rationale:

- Prevents CORS breakage on every new preview deploy.
- Reduces manual configuration and improves template reusability.
- Documented in .env.example and README for future maintainers.

Validation:

- Automated tests for wildcard and regex CORS origins.
- Live deployment verified with multiple preview URLs.

## Consequences

Positive:

- Better reliability of auth, profile hydration, and bootstrap behavior.
- Clear contracts for frontend identity path and backend versioned APIs.
- CI now validates the repository behavior, not only structure.
- Fully operational deployed backend with schema on Railway.

Tradeoffs:

- Hybrid routing requires discipline in endpoint placement.
- Lazy bootstrap introduces first-request write behavior by design.
- CI runtime and local runtime versions must remain intentionally aligned.
- Deployment workflow has two DB URLs (internal for API, public for CLI tools) requiring explicit knowledge.

## Alternatives Considered

- Webhook-first user provisioning instead of lazy bootstrap.
- Fully versioned identity endpoint (`/api/v1/me`) instead of canonical `/api/me`.
- CI validation only on `main` instead of every push.

## Related Artifacts

- `docs/development-logs/4-backend-auth.txt`
- `docs/development-logs/5-postgres.txt`
- `docs/development-logs/6-connect-front2back.txt`
- `docs/development-logs/7-ci.txt`
- `apps/api/app/auth.py`
- `apps/api/app/routes.py`
- `apps/api/app/services/user_bootstrap.py`
- `apps/api/app/core/config.py`
- `.github/workflows/ci.yml`
