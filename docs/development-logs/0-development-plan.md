This document contains references to Cornerstone

I’d drive this in **vertical slices**.

## 1. Stabilize the frontend scaffold

Goal: a clean React app.

- confirm Vite runs
- clean template files
- add Tailwind
- add shadcn/ui
- create basic layout:
  - top bar
  - left nav
  - main content area
  - empty home page

Checkpoint:

```text
localhost:5173 shows generic Cornerstone shell
```

## 2. Add Clerk to the frontend

Goal: users can register/login.

- create Clerk application
- add Clerk env vars
- install Clerk React SDK
- wrap app with Clerk provider
- add sign-in / sign-up routes or components
- protect the app shell

Checkpoint:

```text
logged-out user sees login
logged-in user sees empty homepage
```

## 3. Create the FastAPI backend

Goal: backend exists and can be called.

- create Python project in `apps/api`
- add FastAPI
- add `/health`
- add `/ready`
- add `/version`
- add CORS for local frontend
- add structured error shape

Checkpoint:

```text
curl localhost:8000/health works
frontend can call API health endpoint
```

## 4. Add backend auth verification

Goal: API trusts Clerk tokens.

- frontend sends Clerk session token
- FastAPI validates token
- protected endpoint returns current auth identity
- do not create app user model yet unless needed

Checkpoint:

```text
GET /api/me works only when logged in
```

## 5. Add Postgres locally

Goal: persistent app user/profile foundation.

- Docker Postgres already exists
- add SQLAlchemy
- add Alembic
- create baseline tables:
  - users
  - workspaces
  - workspace_members

- create default user/workspace on first authenticated request

Checkpoint:

```text
login creates local app user + default workspace
```

## 6. Connect frontend to backend

Goal: real logged-in landing page.

- frontend calls `/api/me`
- displays user name/email/avatar if available
- left nav/top nav remain generic
- homepage says something like “Welcome to Cornerstone”

Checkpoint:

```text
authenticated user sees data from backend
```

## 7. Add CI

Goal: every push verifies the repo.

- web lint/typecheck/build
- api lint/test
- optional Docker Compose DB test later

Checkpoint:

```text
GitHub Actions passes
```

## 8. Deploy frontend

Goal: public web URL.

- deploy `apps/web` to Cloudflare Pages
- configure build command
- configure Clerk publishable key
- set API base URL placeholder

Checkpoint:

```text
public URL loads frontend
```

## 9. Deploy backend + database

Goal: public API + hosted Postgres.

- deploy `apps/api` to Railway
- provision Railway Postgres
- set env vars
- run Alembic migrations
- verify `/health`, `/ready`, `/version`

Checkpoint:

```text
public API is reachable and DB-ready
```

## 10. Wire deployed frontend to deployed backend

Goal: full deployed thin slice.

- set frontend API URL to Railway API
- set CORS to Cloudflare Pages URL
- configure Clerk production URLs
- verify login/register
- verify protected homepage

Final checkpoint:

```text
public URL → register/login → protected empty homepage with navigation
```

## Milestone 1 Complete (2026-05-14)

- All vertical slices (frontend, Clerk auth, backend, persistence, CI, deployment) are implemented and validated.
- CORS is now robust: wildcard origin support for Cloudflare Pages preview deploys, no more manual edits needed.
- All tests passing, CI green, and both frontend/backend are live and integrated.
- See /memories/repo/cornerstone-milestone-1.md for a full summary.

## Closeout Notes (2026-05-17)

- Milestone 1 is complete as an end-to-end validation milestone, not as a finished product template.
- The current always-on pull deployment model proved the stack but is provisional for template use; a future ephemeral deploy plus teardown workflow is likely a better fit.
- Clerk remains a valid auth service choice, but the hosted Clerk UI is provisional and expected to be replaced with custom registration, login, and account-management flows in a later milestone.
