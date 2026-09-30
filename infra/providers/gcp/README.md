# GCP Infrastructure Adapter (Not Implemented)

This adapter is a placeholder for future GCP support.

## Workflow Contract

This README is referenced by `docs/setup/repository-adoption.md` Step 9.

Current status:

- GCP adapter is not implemented yet.
- Do not continue cloud provisioning with GCP from this repository state.

Action:

- Return to `docs/setup/repository-adoption.md` Step 9 and select the AWS adapter for active deployment.

## Overview

When implemented, this adapter will follow the same pattern as the AWS adapter:

- **Compute:** Google Cloud Run (managed container service)
- **Frontend:** Google Cloud Storage + Cloud CDN
- **Database:** Cloud SQL PostgreSQL
- **Secrets:** Secret Manager
- **State:** GCS bucket + Cloud Firestore (or Terraform Cloud)
- **Networking:** Minimal VPC setup

## To Implement

1. Create `terraform/modules/` with the same logical modules as AWS
2. Create `terraform/environments/dev/` with main.tf, variables.tf, outputs.tf
3. Create `scripts/bootstrap-state.sh` for GCS state initialization
4. Document setup in this README
5. Update GitHub Actions workflows with GCP-specific secrets and steps

## Reference

See [../aws/README.md](../aws/README.md) for the AWS adapter pattern and [../../README.md](../../README.md) for the provider adapter model.
