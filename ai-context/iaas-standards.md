This document contains references to Cornerstone

# IaaS / Deployment Standards

## Purpose

Cornerstone infrastructure must support repeatable cloud deployment, validation, and teardown.

Cornerstone is not a production product. Its cloud deployment exists to validate that applications built from the template can be provisioned, deployed, tested, and destroyed safely.

## Core Principles

- Prefer Infrastructure as Code over manual portal setup.
- Prefer provider adapters over provider-neutral abstractions.
- Keep application code cloud-neutral.
- Keep provider-specific code isolated under `infra/providers/<provider>`.
- Make teardown a first-class workflow.
- Avoid permanently running infrastructure for Cornerstone unless explicitly required.
- Do not introduce Kubernetes.
- Do not build a private platform layer.
- Optimize for clarity and repeatability over maximum cloud feature usage.

## Provider Adapter Model

Provider-specific infrastructure lives under:

```text
infra/providers/
  aws/
  gcp/
  azure/
```

Only one provider adapter needs to work initially.

Each provider adapter should implement the same lifecycle:

```text
bootstrap
provision
deploy
migrate
smoke-test
teardown
```

## Terraform Standards

- Use Terraform for cloud infrastructure.
- Keep modules small and purpose-specific.
- Avoid clever or deeply nested module structures.
- Prefer explicit variables over implicit assumptions.
- Outputs should map directly to deployment workflow needs.
- Do not store secret values in Terraform variables when avoidable.
- Prefer referencing secret ARNs or parameter names.
- Remote state must be encrypted.
- State locking should be enabled where supported.
- Never commit `.tfstate` files.

## Secrets Standards

- Do not store long-lived AWS access keys in GitHub secrets.
- Prefer GitHub Actions OIDC for cloud authentication.
- Store sensitive runtime secrets in cloud-native secret services.
- For AWS, prefer Secrets Manager for sensitive values.
- Terraform may create secret containers or permissions, but should not own secret values unless explicitly justified.
- Application services should receive secrets at runtime through the provider’s secret injection mechanism.

## GitHub Actions Standards

GitHub Actions owns deployment orchestration.

Workflows should separate:

- CI verification
- cloud-dev deployment
- teardown
- future staging deployment
- future production deployment

Pull requests should verify only.

Merges to `main` may deploy cloud development.

Future release tags may deploy higher environments using patterns such as:

```text
v*.*.*-dev-*
v*.*.*-rc-*
v*.*.*-prod-*
```

Production tags should point to the same commit previously validated as a release candidate.

## Environment Standards

Cornerstone implements only:

- local development
- cloud development

Applications built from Cornerstone may later add:

- staging
- production

Do not implement staging or production inside Cornerstone unless explicitly requested.

## AWS Adapter Expectations

The AWS adapter should provide:

- static frontend hosting
- containerized FastAPI backend hosting
- managed PostgreSQL
- secrets/configuration
- stable service endpoints
- migration execution
- smoke testing
- teardown

Prefer simple AWS services over complex ones.

Avoid:

- Kubernetes/EKS
- multi-account complexity
- advanced networking unless required
- production HA unless explicitly needed

## Docker Standards

- Backend container should be minimal and explicit.
- Do not bake secrets into images.
- Use `.dockerignore` aggressively.
- Dockerfile should support local build and cloud deployment.
- Container must expose health-checkable API endpoints.

## Database Standards

- PostgreSQL remains the default database.
- Migrations use Alembic.
- Deployment workflow must run migrations explicitly.
- Teardown behavior must be documented:
  - destroy database
  - snapshot database
  - preserve database
  - reset schema

For Cornerstone cloud development, disposable database state is acceptable unless otherwise specified.

## Smoke Test Standards

Every deployed cloud-dev environment should validate:

- frontend is reachable
- backend `/health` is reachable
- backend `/ready` is reachable
- backend `/version` is reachable
- database connectivity works
- authenticated flow works when practical

## Cost Standards

- Prefer resources that can scale to zero or be destroyed.
- Keep default instance sizes minimal.
- Do not provision production-grade redundancy for Cornerstone.
- Any always-on cost must be explicitly justified.
- Document estimated monthly cost for idle and active cloud-dev usage.

## Review Checklist

When reviewing infrastructure changes, check:

- Can it be provisioned from a clean environment?
- Can it be destroyed safely?
- Are secrets kept out of source and state where practical?
- Are outputs sufficient for GitHub Actions?
- Are provider-specific concerns isolated?
- Does the app code remain cloud-neutral?
- Are defaults cheap enough for development?
- Is the workflow understandable without portal spelunking?
