This document contains references to Cornerstone

# Infrastructure as Code: Provider Adapter Model

Cornerstone uses a cloud-provider adapter pattern for infrastructure. This allows Cornerstone to remain cloud-neutral while supporting multiple deployment targets (AWS, GCP, Azure).

## Structure

```
infra/
  providers/
    aws/                  # AWS adapter (implemented)
    gcp/                  # GCP adapter (future)
    azure/                # Azure adapter (future)
```

## Usage

Use this directory as a provider adapter index.

Entry point from adoption workflow:

- Start in `docs/setup/repository-adoption.md` Step 9.
- Choose one provider README.
- Complete that provider README end-to-end.
- Return to `docs/setup/repository-adoption.md` Step 10.

### AWS (Current)

To provision and deploy to AWS:

```bash
cd infra/providers/aws

# Step 1: Bootstrap (one-time)
./scripts/bootstrap-state.sh

# Step 2: Provision resources
terraform -chdir=terraform/environments/dev init
terraform -chdir=terraform/environments/dev apply

# Step 3: Deploy application (GitHub Actions manual dispatch)
# Run provision/deploy workflows from the Actions tab
```

See [infra/providers/aws/README.md](providers/aws/README.md) for detailed setup instructions.

### GCP & Azure (Future)

GCP and Azure remain placeholders at this time.

Each provider adapter follows the same pattern:

```
providers/{provider}/
  terraform/
    modules/              # Provider-specific modules
    environments/dev/     # Dev environment configuration
  scripts/
    bootstrap-state.sh    # Provider bootstrap
  README.md              # Setup instructions
```

To add a new provider adapter:

1. Create `providers/{provider}/terraform/modules/` with the same logical module boundaries as AWS (`networking`, `database`, `backend`, `frontend`, `secrets`)
2. Create `providers/{provider}/terraform/environments/dev/` with `main.tf`, `variables.tf`, and `outputs.tf`
3. Mirror key output contracts consumed by workflows (service URL, frontend domain, deployment target IDs, artifact destination names)
4. Create `providers/{provider}/scripts/bootstrap-state.sh` for provider-specific remote state initialization
5. Document setup and provisioning in `providers/{provider}/README.md`
6. Extend GitHub Actions workflows with provider selection logic (or provider-specific workflow variants)

## Deployment Orchestration

GitHub Actions workflows are currently AWS-wired, but organized around a provider-adapter pattern:

- `.github/workflows/deploy-dev.yml` — builds or reuses backend image, deploys backend/frontend, runs smoke checks
- `.github/workflows/teardown-dev.yml` — pause or destroy cloud resources
- `.github/workflows/provision-dev.yml` — initial provisioning

Workflows use GitHub Action secrets and dispatch inputs to pass provider-specific configuration (for AWS: `AWS_ROLE_ARN`, `aws_region`, remote state values, and environment inputs). New providers should preserve this operator model while swapping provider-specific credentials and identifiers.

## Local Development

Local development is unchanged. All developers use `docker-compose.yml` for local database and run the frontend/backend locally without touching cloud infrastructure.

See [docs/setup/local-development.md](../../docs/setup/local-development.md) for details.

## Cost Management

Each provider adapter's costs vary. See the provider-specific README for cost estimates.

**General principle:** Development environments should be pausable (not destroyed) between sessions to preserve configuration and URLs while eliminating compute costs.
