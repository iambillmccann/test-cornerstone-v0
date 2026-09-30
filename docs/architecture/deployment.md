This document contains references to Cornerstone

# Deployment Architecture (AWS Provider Adapter)

This document describes Cornerstone's cloud deployment architecture and how the infrastructure remains portable across providers.

## Provider Adapter Model

Cornerstone uses a provider adapter approach under `infra/providers/{provider}`.

- `infra/providers/aws`: implemented and active
- `infra/providers/gcp`: planned
- `infra/providers/azure`: planned

The application contract remains stable while each provider adapter implements equivalent infrastructure capabilities.

## AWS Service Map (Dev)

Current AWS adapter (`infra/providers/aws`) provisions:

- Networking: VPC, subnets, routing, security groups
- Backend runtime: App Runner service
- Backend container registry: ECR repository
- Database: PostgreSQL on RDS (private)
- Frontend hosting: S3 + CloudFront
- Secrets/config: SSM Parameter Store + Secrets Manager references
- State management: S3 + DynamoDB lock table (bootstrap-managed)

## Environment Lifecycle

Cornerstone defines two lifecycle operations for cloud dev:

1. Provision: create/update resources via Terraform (`provision-dev.yml`)
2. Deploy: ship backend/frontend artifacts to provisioned resources (`deploy-dev.yml`)
3. Teardown pause: stop/scale down mutable services while preserving resource shape and URLs (`teardown-dev.yml`, mode `pause`)
4. Teardown destroy: full Terraform destroy for the environment state (`teardown-dev.yml`, mode `destroy`)

Notes:

- This is Terraform-state-driven lifecycle management, not CloudFormation stack deletion.
- Bootstrap-managed assets (remote state infra/secrets bootstrap) are not part of normal app-environment destroy.

## Portability Design Principles

Provider portability is achieved by keeping boundaries explicit:

- Application code does not import provider SDKs for runtime deployment concerns.
- Provider-specific resource definitions stay under the relevant adapter directory.
- Equivalent module responsibilities are preserved across providers:
  - `networking`
  - `database`
  - `backend`
  - `frontend`
  - `secrets`

When adding GCP or Azure, preserve output contracts expected by CI workflows (service URL, frontend domain, storage target, deployment target IDs), then adapt workflow logic by provider.

## CI/CD Relationship

- `provision-dev.yml`: Terraform apply against the AWS adapter/environment
- `deploy-dev.yml`: backend image build/reuse + App Runner deploy + frontend publish + smoke checks
- `teardown-dev.yml`: reversible pause or destructive destroy
- `ci.yml`: code quality + Terraform fmt/validate checks

This split keeps infrastructure provisioning, application deployment, and environment lifecycle controls separate and auditable.
