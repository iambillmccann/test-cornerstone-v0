This document contains references to Cornerstone

# 0004: Infrastructure as Code Deployment Adapter Model

## Decision

Cornerstone will move from platform-pull deployment (Cloudflare/Railway auto-deploy on push) to explicit Infrastructure as Code (IaC) deployment orchestrated by GitHub Actions, starting with AWS as the first provider adapter.

### Update: June 6, 2026 — Frontend Shell UX and PWA Baseline

The template baseline now also standardizes frontend shell behavior for authenticated users:

- Left sidebar is primary navigation only (Home in current baseline)
- Account-related actions live in a top-right avatar dropdown (Settings, Account, Sign out)
- Sign-out action continues using Clerk signOut with redirect to /sign-in

Cornerstone web is now configured as a Progressive Web App (PWA) using Vite PWA integration.

PWA policy for this template is online-first and auth-safe:

- NetworkOnly for API and Clerk/auth-related requests
- StaleWhileRevalidate for static assets
- NetworkFirst for non-API page navigations

This improves installability and shell performance while avoiding cached auth/session/API behavior that could cause stale or insecure state for SaaS usage.

### Manual Step 1: AWS OIDC Trust Setup (Complete)

The AWS account, IAM OIDC provider, and GitHub ↔ AWS trust relationship are now established. This enables secure, keyless authentication for GitHub Actions deployments.

**Commands used:**

1. Create OIDC provider:
   ```bash
   aws iam create-open-id-connect-provider \
     --url "https://token.actions.githubusercontent.com" \
     --client-id-list "sts.amazonaws.com" \
     --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1" \
     --profile cornerstone
   ```
2. Create trust policy file (substitute your AWS account ID):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Federated": "arn:aws:iam::<account-id>:oidc-provider/token.actions.githubusercontent.com"
         },
         "Action": "sts:AssumeRoleWithWebIdentity",
         "Condition": {
           "StringLike": {
             "token.actions.githubusercontent.com:sub": "repo:fourier-gauss-labs/cornerstone:*"
           },
           "StringEquals": {
             "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
           }
         }
       }
     ]
   }
   ```
3. Create IAM role:
   ```bash
   aws iam create-role --role-name github-actions-cornerstone-deploy \
     --assume-role-policy-document file:///tmp/cornerstone-github-trust.json \
     --profile cornerstone --output json
   ```
4. Attach permissions:
   ```bash
   aws iam attach-role-policy --role-name github-actions-cornerstone-deploy \
     --policy-arn arn:aws:iam::aws:policy/AdministratorAccess \
     --profile cornerstone
   ```
5. Copy the role ARN (e.g., `arn:aws:iam::098295335350:role/github-actions-cornerstone-deploy`) and add as `AWS_ROLE_ARN` in GitHub repository secrets.

---

### Infrastructure Provisioning: AWS

**Compute & Hosting:**

- Frontend: AWS S3 + CloudFront (static site hosting with HTTPS and SPA routing)
- Backend: AWS App Runner (managed container service with stable URL, pause/resume capability)
- Database: Amazon RDS PostgreSQL 16 (t4g.micro, private access from backend only)

**Secrets & Configuration:**

- Secrets Manager: stores CLERK_SECRET_KEY and DATABASE_URL; created by bootstrap script (not managed by Terraform)
- SSM Parameter Store: stores non-sensitive config (CLERK*JWKS_URL, CORS_ORIGINS, VITE*\* build vars)
- No sensitive values ever land in Terraform state; secrets are referenced by ARN only
- Clerk issuer/audience are optional for compatibility but recommended for strict JWT validation

**Networking:**

- VPC with 2 public subnets (App Runner, NAT Gateway) and 2 private subnets (RDS)
- NAT Gateway enables backend outbound internet access (required for Clerk API calls)
- Security groups restrict RDS inbound to App Runner VPC connector only
- Private RDS access improves security posture for dev environment

### Infrastructure as Code: Terraform

**Provider Adapter Structure:**

```
infra/providers/
  aws/
    terraform/
      modules/            # ecr, frontend, backend, database, networking, secrets
      environments/dev/   # dev environment configuration + remote state backend
    scripts/
      bootstrap-state.sh  # one-time: S3 state bucket + DynamoDB + Secrets Manager
  gcp/
    README.md            # Placeholder (not implemented)
  azure/
    README.md            # Placeholder (not implemented)
```

**State Management:**

- Remote backend: S3 bucket + DynamoDB lock table (created by bootstrap script, never managed by Terraform)
- State bucket is encrypted at rest and has versioning enabled
- S3 state bucket is preserved through all destroy operations (bootstrap infrastructure)
- Resource grouping is Terraform-state driven, not AWS-stack driven; teardown happens via Terraform plus shared tags/name prefixes rather than deleting a single CloudFormation stack

### Deployment Orchestration: GitHub Actions

**Workflows:**

1. **ci.yml** (implemented): web, API, and Terraform fmt/validate checks
2. **provision-dev.yml** (implemented): Manual dispatch — runs Terraform apply for the AWS dev environment
3. **deploy-dev.yml** (implemented): Manual dispatch

- Builds Docker image and pushes to ECR
- Starts App Runner deployment
- Builds frontend and deploys to S3 + CloudFront invalidation
- Runs smoke tests (frontend root + backend health)
- Uses backend image tags `sha-<GITHUB_SHA>` and `latest`
- Reuses existing SHA-tagged backend images when available, with optional force rebuild override
- Ensures `/cornerstone-dev/cors_origins` includes the current CloudFront origin before backend redeploy
- Treats App Runner `ROLLBACK_SUCCEEDED` as terminal deployment failure in wait logic

Implementation note:

- Workflow files include an explicit GitHub workflow schema hint to improve editor diagnostics stability.

4. **teardown-dev.yml** (implemented): Manual dispatch with mode input
   - `pause` (default): pauses App Runner, stops RDS, empties S3 (preserves all URLs and Clerk config)

- `destroy`: runs `terraform destroy` (full nuke; requires Clerk config update on next provision)
- optional `keep_ecr_repository=true`: detaches ECR resources from Terraform state before destroy so the repository is preserved

Provisioning behavior refinement (May 2026):

- `provision-dev.yml` performs an early ECR bootstrap/push of a minimal placeholder image so initial App Runner service creation can pull `latest`.
- `provision-dev.yml` syncs `DATABASE_URL` secret content from the live RDS-managed master credentials before App Runner creation.
- `DATABASE_URL` format includes `sslmode=require` for private RDS/App Runner runtime connectivity.

5. **migrate.yml** (planned): Manual dispatch — database migration execution from inside the AWS network boundary

**Current constraint:**

- GitHub-hosted runners cannot reach the current private RDS instance directly, so database migration execution is not yet part of `deploy-dev.yml`.
- Teardown `destroy` currently follows Terraform state scope; bootstrap-managed state resources and bootstrap-created secrets remain outside this workflow.
- When ECR preservation is used, subsequent Terraform apply may require importing preserved ECR resources into state.

### Stable URLs and Clerk Configuration

**App Runner URL** (e.g., `https://{id}.{region}.awsapprunner.com`):

- Stable across pause/resume cycles (no URL change)
- Only changes if service is destroyed (destroy mode teardown)

**CloudFront URL** (e.g., `https://{id}.cloudfront.net`):

- Stable across S3 content updates
- Only changes if distribution is destroyed (destroy mode teardown)

**Clerk Configuration** (set once during provisioning):

- Allowed origins: CloudFront URL
- Redirect URLs: CloudFront URL for signup/signin, App Runner URL for callback
- CORS_ORIGINS SSM parameter: set to CloudFront URL

**Implications:**

- `pause` mode teardown keeps all URLs constant → no Clerk dashboard updates needed on redeploy
- `destroy` mode teardown is a full reset → Clerk dashboard must be updated with new URLs on next provision

### Docker Container

**Image:** `python:3.12-slim` base (matches local Python 3.12 version)

- Runs: `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Reads secrets from environment (injected by App Runner from Secrets Manager)

### Authentication: GitHub OIDC

- GitHub Actions authenticates to AWS via OpenID Connect (no long-lived access keys)
- One-time setup: create IAM OIDC provider for GitHub in AWS
- GitHub Actions secrets store only the OIDC role ARN and AWS region
- For local operator setup, shell variables should be project-scoped via `source scripts/aws-env.sh` (avoid global `~/.bashrc` coupling)
- AWS Toolkit (VS Code) may show multiple enabled regions in Explorer; deployment commands should still use explicit profile/region in CLI when validating setup

### Provider Portability

The architecture is designed for future GCP and Azure adapters:

- Application code remains cloud-neutral
- Provider-specific infrastructure lives under `infra/providers/{provider}/`
- Deployment orchestration (GitHub Actions) is provider-agnostic
- Each provider has its own `environments/dev/` with provider-specific resources

## Constraints & Assumptions

- AWS account already exists with admin access
- Clerk must be environment-isolated: `cornerstone-local` for local and `cornerstone-dev` for AWS dev
- Native App Runner + CloudFront URLs used (custom domain optional, future enhancement)
- Existing Railway/Cloudflare deployment remains intact during this phase
- RDS is private and only accessible from backend service (security by design, not just acceptable for dev)
- Secrets Manager secrets created by bootstrap script outside Terraform (avoid sensitive values in state)
- All infrastructure changes must go through Terraform (no manual console changes)
- Clerk issuer and audience are optional fields for initial compatibility (recommended to populate for strict JWT validation)

### Clerk Environment Isolation

Cornerstone local and cloud dev environments use separate databases and should therefore use separate Clerk applications to avoid cross-environment identity coupling.

Policy:

- local: `cornerstone-local`
- cloud dev: `cornerstone-dev`

Operational implications:

- local env files carry only `cornerstone-local` values
- cloud dev provisioning inputs and AWS-managed config carry only `cornerstone-dev` values
- Clerk allowed origins and redirect URLs must be configured per environment and never shared

## Cost Implications

- **Running**: ~$18–35/month (App Runner + RDS + misc)
- **Paused**: ~$3–5/month (RDS storage + Secrets Manager only)
- **Full destroy**: ~$0/month (only state S3 bucket remains)

Recommendation: use `pause` mode between validation sessions.

## Operator Scripts

`scripts/cloud-status.sh <aws|azure|gcp>`

- Checks the running state of cloud resources for the current project without knowing any URLs.
- For `aws`: reads `GITHUB_REPO` from `scripts/aws-env.sh` to build the resource name filter, then queries App Runner for matching services.
- For `azure` / `gcp`: prints a not-yet-supported message.
- Template portable: derived apps set their own `GITHUB_REPO` in `aws-env.sh`; the script requires no further changes.

## Not Included (Future)

- Staging and production environments (documented as future tag strategy)
- Custom domain / Route53
- GCP and Azure adapters (structure and placeholders only)
- Kubernetes or ECS (deliberately avoided)

## Reference

See implementation plan in `/memories/session/plan.md` and development log in `docs/development-logs/9-iaas-refactor.txt`.
