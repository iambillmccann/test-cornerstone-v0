# Azure Infrastructure Adapter (Not Implemented)

This adapter is a placeholder for future Azure support.

## Workflow Contract

This README is referenced by `docs/setup/repository-adoption.md` Step 9.

Current status:

- Azure adapter is not implemented yet.
- Do not continue cloud provisioning with Azure from this repository state.

Action:

- Return to `docs/setup/repository-adoption.md` Step 9 and select the AWS adapter for active deployment.

## Overview

When implemented, this adapter will follow the same pattern as the AWS adapter:

- **Compute:** Azure Container Instances or Azure App Service
- **Frontend:** Azure Static Web Apps or Azure Blob Storage + Azure CDN
- **Database:** Azure Database for PostgreSQL
- **Secrets:** Azure Key Vault
- **State:** Azure Storage Account (Blob)
- **Networking:** Minimal VNet setup

## To Implement

1. Create `terraform/modules/` with the same logical modules as AWS
2. Create `terraform/environments/dev/` with main.tf, variable.tf, outputs.tf
3. Create `scripts/bootstrap-state.sh` for Azure Storage state initialization
4. Document setup in this README
5. Update GitHub Actions workflows with Azure-specific secrets and steps

## Reference

See [../aws/README.md](../aws/README.md) for the AWS adapter pattern and [../../README.md](../../README.md) for the provider adapter model.
