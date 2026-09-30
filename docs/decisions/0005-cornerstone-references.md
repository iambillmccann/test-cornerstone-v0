This document contains references to Cornerstone

# 0005: Cornerstone Reference Residual Audit

## Status

Accepted

## Date

2026-06-30

## Context

Cornerstone is a template scaffold. References to Cornerstone must be replaceable for downstream applications without breaking current Cornerstone behavior, tests, or deployments.

A first implementation pass parameterized runtime/build/infra/workflow naming and added a rename script. This decision records the second hardening pass and a residual-reference audit.

## Script Hardening (Second Pass)

The rename utility [scripts/scaffold-rebrand.sh](../../scripts/scaffold-rebrand.sh) was hardened to reduce accidental replacements:

1. Added explicit CLI handling:

- `--dry-run`
- `--verbose`
- `--help`

2. Added explicit in-scope file classification:

- Processes tracked files with known text/config/code extensions.
- Skips known runtime/build artifacts (`.git`, `.venv`, `.terraform`, `node_modules`).

3. Made replacements deterministic and source-anchored:

- Replaces from canonical source literals (`Cornerstone`, `cornerstone`, `cornerstone-api`, `github-actions-cornerstone-deploy`, `API_VERSION=0.1.0`).
- No longer derives the source role-name pattern from target values.

4. Added safe escaping for replacement values:

- Uses escaped regex-safe values for all replacements.

## Residual Reference Audit

### Method

Audit search used case-sensitive matches for `Cornerstone|cornerstone` across tracked repository content, excluding `.git`, `.venv`, `.terraform`, and `node_modules` for the top-level total.

### Summary Table

| Category                                                          | Count | Intent                            | Representative references                                                                                                                                                                                                                                                                                                                      | Disposition                                                                                                       |
| ----------------------------------------------------------------- | ----: | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| Canonical defaults and parameter anchors                          |    55 | Intentional                       | [scaffold.env](../../scaffold.env), [.env.example](../../.env.example), [apps/web/vite.config.ts](../../apps/web/vite.config.ts), [.github/workflows/deploy-dev.yml](../../.github/workflows/deploy-dev.yml), [infra/providers/aws/terraform/environments/dev/variables.tf](../../infra/providers/aws/terraform/environments/dev/variables.tf) | Keep as default baseline for backward compatibility; replace via scaffold/env/workflow inputs for downstream apps |
| Cornerstone-specific docs (non-log)                               |   112 | Intentional                       | [README.md](../../README.md), [docs/decisions/0004-iaas-refactor.md](0004-iaas-refactor.md), [docs/setup/authentication.md](../setup/authentication.md), [infra/providers/aws/README.md](../../infra/providers/aws/README.md)                                                                                                                  | Keep; all such docs now include required marker line                                                              |
| Marker lines (`This document contains references to Cornerstone`) |    27 | Intentional policy marker         | [README.md](../../README.md), [docs/architecture/overview.md](../architecture/overview.md), [ai-context/product-brief.md](../../ai-context/product-brief.md)                                                                                                                                                                                   | Keep exactly as required by policy                                                                                |
| Historical development logs                                       |    47 | Intentional historical record     | [docs/development-logs/9-iaas-refactor.txt](../development-logs/9-iaas-refactor.txt), [docs/development-logs/3-fastapi.txt](../development-logs/3-fastapi.txt)                                                                                                                                                                                 | Keep for traceability/history                                                                                     |
| Test fixtures and assertions                                      |     9 | Intentional verification baseline | [apps/api/tests/test_endpoints.py](../../apps/api/tests/test_endpoints.py), [apps/api/tests/test_cors_settings.py](../../apps/api/tests/test_cors_settings.py)                                                                                                                                                                                 | Keep to validate default scaffold identity behavior                                                               |
| Generated tracked artifacts                                       |    17 | Intentional derived output        | [apps/web/dist/index.html](../../apps/web/dist/index.html), [apps/web/dist/manifest.webmanifest](../../apps/web/dist/manifest.webmanifest), [apps/web/dist/sw.js](../../apps/web/dist/sw.js), [apps/api/cornerstone_api.egg-info/PKG-INFO](../../apps/api/cornerstone_api.egg-info/PKG-INFO)                                                   | Keep in sync with source defaults; regenerated on build/package steps                                             |
| Live environment-specific tfvars secret ARNs                      |     2 | Intentional deployment binding    | [infra/providers/aws/terraform/environments/dev/terraform.tfvars](../../infra/providers/aws/terraform/environments/dev/terraform.tfvars)                                                                                                                                                                                                       | Keep for current deployed environment; expected to differ per fork/environment                                    |

### Top-Level Residual Count

- Total residual references after refactor pass: **264**

## Decision

Residual references are acceptable when they are one of:

1. Canonical default values needed to preserve current Cornerstone behavior.
2. Cornerstone-specific documentation/history where references are accurate context.
3. Generated artifacts derived from current default naming.
4. Environment-bound deployment values (for the existing dev environment).

No additional blanket replacement is approved beyond these categories.

## Consequences

1. New applications can rebrand by updating [scaffold.env](../../scaffold.env) and running [scripts/scaffold-rebrand.sh](../../scripts/scaffold-rebrand.sh).
2. Cornerstone continues to run unchanged with current defaults.
3. Future audits should treat this table as the residual allowlist baseline.
