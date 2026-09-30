# Future Environments Strategy (Documented, Not Yet Implemented)

This document defines the intended tag and branch strategy for environments beyond cloud `dev`.

Status: documented only. Staging and production workflow automation is not implemented yet.

## Planned Promotion Rules

- `main` branch merge: deploy cloud `dev`
- `v*.*.*-dev-*` tag: deploy cloud `dev`
- `v*.*.*-rc-*` tag: deploy `staging` (planned)
- `v*.*.*-prod-*` tag: deploy `production` (planned)

## Release Integrity Requirement

Production tags must reference the same commit that was validated in the corresponding release-candidate deployment.

In other words:

1. Deploy and validate RC commit in staging
2. Promote that exact commit to production via `v*.*.*-prod-*` tag
3. Do not retag a different commit as production for the same release line

## Why This Matters

- Reduces drift between tested and released artifacts
- Preserves auditability of release promotions
- Supports reproducible rollbacks and incident analysis

## Implementation Notes (Future)

When implemented, workflows should enforce:

- Environment-specific approval gates
- Required smoke/integration checks before promotion
- Tag-to-commit verification from RC to production
- Clear run summaries for artifact/image identifiers used in each environment
