This document contains references to Cornerstone

# Cloud Development Operations

This runbook covers first-time setup and daily operations for the cloud `dev` environment on AWS.

## First-Time Setup

1. Configure AWS OIDC trust between GitHub Actions and AWS.
2. Bootstrap Terraform remote state infrastructure (S3 bucket + DynamoDB lock table).
3. Ensure required repository secret exists:
   - `AWS_ROLE_ARN`
4. Prepare workflow-dispatch values for:
   - `aws_region`
   - `tf_state_bucket`
   - `tf_state_key`
   - `environment_name`
   - Clerk and app config values required by `provision-dev.yml`

## Provision Workflow

Use `.github/workflows/provision-dev.yml` to create/update infrastructure.

Expected outcomes:

- Terraform apply succeeds
- Infrastructure outputs are available (App Runner URL, CloudFront domain, ECR repo, etc.)
- SSM/Secrets references are wired for deploy-time usage

## Deploy Workflow

Use `.github/workflows/deploy-dev.yml` after provision.

Deploy behavior:

- Resolves Terraform outputs
- Uses backend image tag `sha-<GITHUB_SHA>` (also updates `latest`)
- Reuses existing SHA-tagged image unless `force_backend_rebuild=true`
- Triggers App Runner deployment
- Builds and publishes frontend to S3 + CloudFront invalidation
- Runs smoke checks for:
  - frontend HTTP 200
  - `/api/v1/health`
  - `/api/v1/ready`
  - `/api/v1/version`
  - CORS header presence for frontend origin

## Teardown Workflow

Use `.github/workflows/teardown-dev.yml`.

Modes:

- `pause`: pause App Runner, stop RDS if available, clear frontend bucket content, invalidate CloudFront
- `destroy`: Terraform destroy of environment-managed resources

Optional behavior in destroy mode:

- `keep_ecr_repository=true` detaches ECR resources from Terraform state before destroy so image history can be retained

## Clerk Config Update Procedure

When Clerk values change, update environment configuration through the same path used by provisioning inputs and re-run provision/deploy as needed.

Typical sequence:

1. Update Clerk values used by `provision-dev.yml` inputs.
2. Run `provision-dev.yml` to persist config updates.
3. Run `deploy-dev.yml` to roll app artifacts with updated runtime/build config.
4. Re-run smoke checks via deploy workflow result.

## Known Constraints

- GitHub-hosted runners cannot directly reach private RDS for migration execution.
- Database migrations are currently not performed from `deploy-dev.yml`.
- Authenticated `/api/me` smoke check is deferred until a stable CI strategy for Clerk session token injection is added.

## Environment Isolation Reset Runbook

Use this runbook when local development and cloud dev were pointed at the same Clerk application and you want clean environment separation.

Goal:

- `cornerstone-local` Clerk app drives local development only.
- `cornerstone-dev` Clerk app drives AWS `dev` environment only.
- Local PostgreSQL and cloud RDS remain independent, with auth identities isolated per environment.

### 1) Local Teardown

1. Stop local API/web processes (`Ctrl+C` in dev terminals).
2. Reset local PostgreSQL data from repo root:

```bash
./scripts/dev-db-reset.sh
```

3. Clear old local Clerk values in local env files before re-populating:
   - `.env.local` (repo root)
   - `apps/web/.env.local`
   - `apps/api/.env` (if present)

Recommended quick reset pattern:

```bash
cp .env.example .env.local
cp apps/api/.env.example apps/api/.env
```

Then set fresh values after Clerk apps are recreated.

### 2) AWS Teardown

Run teardown workflow `.github/workflows/teardown-dev.yml` in `destroy` mode with:

- `mode=destroy`
- `confirm_destroy=DESTROY`
- `aws_region`, `tf_state_bucket`, `tf_state_key`, `environment_name`
- optional `keep_ecr_repository` as needed

Post-run checks:

1. Confirm workflow succeeded.
2. Confirm app resources are gone (App Runner/RDS/CloudFront/S3 tracked by Terraform state).
3. Confirm bootstrap resources are intentionally handled:
   - state bucket + lock table remain (expected)
   - bootstrap-managed secrets remain unless you explicitly rotate/reset them

### 3) Clerk Reset

In Clerk dashboard:

1. Delete old shared Cornerstone app.
2. Create `cornerstone-local`.
3. Create `cornerstone-dev`.

For each app, capture:

- publishable key
- secret key
- JWKS URL
- issuer (optional but recommended)
- audience (optional, if your token template uses it)

### 4) Reconfigure Environment Values

Local (`cornerstone-local`):

- `.env.local`:
  - `CLERK_PUBLISHABLE_KEY`
  - `CLERK_SECRET_KEY`
  - `CLERK_JWKS_URL`
  - `CLERK_ISSUER`
  - `CLERK_AUDIENCE`
- `apps/web/.env.local`:
  - `VITE_CLERK_PUBLISHABLE_KEY` (must match local Clerk app)
  - `VITE_API_BASE_URL=http://localhost:8000`
- `apps/api/.env`:
  - `CLERK_JWKS_URL`
  - optional `CLERK_ISSUER`
  - optional `CLERK_AUDIENCE`
  - local `CORS_ORIGINS`

Cloud dev (`cornerstone-dev`):

1. Rotate/update AWS Secrets Manager entries used by Terraform inputs:
   - `clerk_secret_key_arn` target secret value
2. Run `.github/workflows/provision-dev.yml` with `cornerstone-dev` values:
   - `clerk_jwks_url`
   - optional `clerk_issuer`
   - optional `clerk_audience`
   - `clerk_publishable_key`
   - `clerk_secret_key_arn`
   - `rds_database_url_arn`
   - `cors_origins` set to CloudFront URL once known

Clerk dashboard URL/origin alignment:

- `cornerstone-local` allowed origins + redirects: localhost URLs only.
- `cornerstone-dev` allowed origins + redirects: CloudFront + App Runner URLs only.

### 5) Rebuild Upward

Local first:

1. Start DB/API/web locally.
2. Log in via `cornerstone-local`.
3. Verify first authenticated call creates local user/workspace records.

Cloud dev second:

1. Run `provision-dev.yml` (if needed for config/state refresh).
2. Run `deploy-dev.yml`.
3. Log in via `cornerstone-dev`.
4. Verify first authenticated call creates cloud-dev user/workspace records.

Success criteria:

- A local login never appears in cloud-dev DB.
- A cloud-dev login never appears in local DB.
- Clerk session/token metadata reflects the expected environment-specific app.
