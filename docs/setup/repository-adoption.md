# Repository Adoption Guide

This guide explains how to take a fresh clone of this repository and turn it into a rebranded application that runs locally and on a chosen cloud provider adapter.

Current implementation status: AWS is the only fully implemented provider adapter. Azure and GCP remain placeholders.

This guide intentionally refers to the template repository during setup. The goal is that, after you complete the steps below, your adopted repository no longer contains template-name references in code, configuration, documentation, or deployment settings.

## 1. Prerequisites

Install or configure the following before making changes:

- Git
- Docker
- Python 3.11+
- Node.js 20.19+
- npm
- AWS CLI
- Terraform 1.7+
- A Clerk account
- A GitHub repository for the new application

## 2. Clone the Repository

Clone the repository and enter it:

```bash
git clone <your-repository-url>
cd <your-repository-folder>
```

## 3. Set the New Application Identity

Edit the root file `scaffold.env`.

Note: this file is sourced by Bash. Any value containing spaces must be wrapped in double quotes.

Set these values:

- `APP_SLUG`: lowercase, hyphenated application name
- `APP_DISPLAY_NAME`: user-facing application name
- `API_NAME`: backend service name, usually `<app-slug>-api`
- `API_VERSION`: keep `0.1.0` unless you want a different initial version
- `DATABASE_NAME`: local/AWS database name
- `AWS_PROFILE`: local AWS CLI profile name
- `GITHUB_OWNER`: GitHub organization or username
- `GITHUB_REPO`: repository name
- `AWS_ROLE_NAME`: IAM role name for GitHub Actions OIDC deploys

Note: `AWS_ROLE_NAME` is only the IAM role name used for naming and scaffolding. It is not the value you put into the GitHub secret `AWS_ROLE_ARN`.

Example:

```dotenv
APP_SLUG=acme-portal
APP_DISPLAY_NAME="Acme Portal"
API_NAME=acme-portal-api
API_VERSION=0.1.0
DATABASE_NAME=acme_portal
AWS_PROFILE=acme-portal
GITHUB_OWNER=your-org
GITHUB_REPO=acme-portal
AWS_ROLE_NAME=github-actions-acme-portal-deploy
```

Later, when configuring GitHub Actions, set `AWS_ROLE_ARN` to the full IAM role ARN, for example `arn:aws:iam::123456789012:role/github-actions-acme-portal-deploy`. In the AWS path, Terraform now creates that role and outputs the ARN for you.

## 4. Preview and Apply Rebranding

Preview the changes:

```bash
./scripts/scaffold-rebrand.sh --dry-run
```

Apply the changes:

```bash
./scripts/scaffold-rebrand.sh
```

Verify that the previous template name is gone by searching for the old display name and old slug:

```bash
grep -RIn --exclude-dir=.git --exclude-dir=.venv --exclude-dir=node_modules --exclude-dir=.terraform -E 'OLD_DISPLAY_NAME|old-slug' .
```

If any matches remain, review them before continuing.

## 5. Create Authentication Applications

Create two separate Clerk applications:

- one for local development
- one for AWS dev

For each Clerk application, collect:

- publishable key
- secret key
- JWKS URL
- issuer URL if used
- audience if used

Configure allowed origins and redirect URLs separately for local and AWS.

## 6. Configure Local Environment Files

Create local environment files from the provided examples.

Repository root:

```bash
cp .env.example .env.local
```

Backend:

```bash
cp apps/api/.env.example apps/api/.env
```

Set the root `.env.local` values:

- `APP_NAME`
- `APP_DISPLAY_NAME`
- `APP_SLUG`
- `APP_ENV=local`
- `API_NAME`
- `POSTGRES_DB`
- `DATABASE_URL`
- `CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `CLERK_JWKS_URL`
- optional `CLERK_ISSUER`
- optional `CLERK_AUDIENCE`

Recommended values:

- `APP_NAME=<app-slug>`
- `APP_DISPLAY_NAME=<display name>`
- `APP_SLUG=<app-slug>`
- `API_NAME=<app-slug>-api`
- `POSTGRES_DB=<database name>`
- `DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/<database name>`

Set `apps/api/.env` values:

- `APP_NAME=<app-slug>-api`
- `APP_SLUG=<app-slug>`
- `API_NAME=<app-slug>-api`
- `APP_VERSION=0.1.0`
- `DATABASE_NAME=<database name>`
- `CLERK_JWKS_URL`
- optional `CLERK_ISSUER`
- optional `CLERK_AUDIENCE`
- optional `DATABASE_URL`

Create `apps/web/.env.local` with:

```dotenv
VITE_APP_SLUG=<app-slug>
VITE_APP_DISPLAY_NAME=<display name>
VITE_APP_DESCRIPTION=<short app description>
VITE_API_NAME=<app-slug>-api
VITE_CLERK_PUBLISHABLE_KEY=<local Clerk publishable key>
VITE_API_BASE_URL=http://localhost:8000
```

## 7. Start Local Development

### 7.1 Start PostgreSQL

From the repository root:

```bash
./scripts/dev-db-up.sh
```

### 7.2 Install and Prepare the Backend

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
alembic upgrade head
```

### 7.3 Install the Frontend

```bash
cd apps/web
npm install
```

### 7.4 Run the Backend

```bash
cd apps/api
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

### 7.5 Run the Frontend

```bash
cd apps/web
npm run dev
```

### 7.6 Verify Local Startup

Open:

- frontend: `http://localhost:5173`
- backend health endpoint: `http://127.0.0.1:8000/api/v1/health`

Check that:

- the frontend title and visible branding use the new application name
- sign-in and sign-up pages load
- the backend health endpoint returns success

## 8. Optional Local Reset Commands

Stop the database:

```bash
./scripts/dev-db-down.sh
```

Reset local database state:

```bash
./scripts/dev-db-reset.sh
cd apps/api
source .venv/bin/activate
alembic upgrade head
```

## 9. Prepare Cloud Access

Treat provider setup as a reusable adapter runbook.

### 9.1 Select Provider Runbook

Choose one provider README and complete it end-to-end:

- AWS (implemented): `infra/providers/aws/README.md`
- Azure (placeholder, unsupported): `infra/providers/azure/README.md`
- GCP (placeholder, unsupported): `infra/providers/gcp/README.md`

### 9.2 Complete Setup in the Selected Provider README

The selected provider README is the source of truth for cloud setup details.

For AWS, this includes (at minimum):

- loading project-scoped cloud variables
- creating GitHub OIDC trust
- adding the required GitHub repository secret(s)
- handling first-run OIDC bootstrap sequencing (a role must already be assumable before Terraform can manage the final role)
- bootstrapping Terraform state/secrets
- provisioning cloud infrastructure
- deploying the application
- validating cloud deployment endpoints

### 9.3 Return to This Guide

When provider setup is complete, return here and continue with the next section.

## 10. Recommended Final Verification

Run these checks after rebranding and setup:

```bash
cd apps/api
source .venv/bin/activate
pytest
```

```bash
cd apps/web
npm run build
```

Then search one more time for the previous template name and slug:

```bash
grep -RIn --exclude-dir=.git --exclude-dir=.venv --exclude-dir=node_modules --exclude-dir=.terraform -E 'OLD_DISPLAY_NAME|old-slug' .
```

The result should be empty.

If you want to verify removal of template references specifically, search for the template display name and slug that existed before rebranding and confirm the result is empty or limited only to documents you still intend to keep temporarily.

## 11. Final Cleanup

After local and cloud verification succeeds, clean up any template-specific adoption artifacts you no longer want to keep.

Recommended final actions:

1. Remove or rewrite any template-specific notes that are no longer useful for your application.
2. Re-run your repository-wide search for the former template name and slug.
3. If this guide is no longer needed in the adopted repository, delete it.

Example:

```bash
rm docs/setup/repository-adoption.md
```

## 12. Files and Scripts Used in This Process

Core configuration files:

- `scaffold.env`
- `.env.example`
- `.env.local`
- `apps/api/.env.example`
- `apps/api/.env`
- `apps/web/.env.local`
- `infra/providers/aws/README.md`
- `infra/providers/azure/README.md`
- `infra/providers/gcp/README.md`

Scripts:

- `./scripts/scaffold-rebrand.sh`
- `./scripts/dev-db-up.sh`
- `./scripts/dev-db-down.sh`
- `./scripts/dev-db-reset.sh`
- provider-specific scripts listed in the selected provider README

GitHub Actions workflows:

- `.github/workflows/provision-dev.yml`
- `.github/workflows/deploy-dev.yml`
- `.github/workflows/teardown-dev.yml`
