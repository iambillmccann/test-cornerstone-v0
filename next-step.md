# Cornerstone vNext Hardening Backlog

## Goal

Reduce time from fresh repo adoption to first successful cloud deploy from about two weeks to one to two days, and make one-week app delivery realistic.

## Context

LockedOnIt validated the full lifecycle end-to-end:

- Provision completed
- Deploy completed
- Teardown completed
- Auth worked for email and Microsoft OAuth

This confirms the architecture is viable. The remaining work is productizing the setup experience.

## Success Metrics

- Time to first successful provision in a new repo: less than 2 hours
- Time to first successful deploy in a new repo: less than 1 day
- Zero manual AWS console steps required in normal path
- Clear failure messages for top 10 setup errors
- New adopter can complete setup by following docs only

## Operating Principles

- Prefer fail-fast validation over late runtime failures
- Make the golden path explicit and short
- Keep one source of truth per concern
- Treat setup friction as product defects
- Automate anything repeated more than once

## Priority 0: Blockers and High-Leverage Fixes

### 1. Preflight command for environment sanity

Problem:
Most delays came from profile/account/region/ARN mismatches.

Deliverable:
Add one preflight command that checks:

- Active AWS account id
- Expected account id for environment
- AWS profile and region
- Existence of required backend resources
- Presence and format of required secrets and variables
- OIDC provider presence
- Existence of GitHub role

Acceptance criteria:

- Returns pass or fail with actionable messages
- Fails in under 30 seconds
- Called before provisioning in docs and workflows

Estimate:

- 0.5 to 1 day

### 2. OIDC bootstrap deadlock removal

Problem:
Provision workflow requires role assumption before Terraform can create role.

Deliverable:
Formalize bootstrap sequence and automate fallback behavior where possible:

- Reuse existing OIDC provider if present
- Create role only when missing
- Surface clear guidance when bootstrap role is required

Acceptance criteria:

- No ambiguous AssumeRoleWithWebIdentity errors
- User gets a deterministic next step from logs
- Bootstrap flow documented in one concise section

Estimate:

- 0.5 day

### 3. Workflow input and secret validation hardening

Problem:
Bad inputs fail late and cost hours.

Deliverable:
Add strict validation at workflow start:

- ARN pattern checks
- Required input completeness
- Region consistency checks
- Optional guard: role account id must match selected backend account

Acceptance criteria:

- Validation fails before any terraform or docker work
- Error text includes exact corrective action

Estimate:

- 0.5 day

### 4. Golden path quickstart

Problem:
Current guidance is thorough but still too broad for first run.

Deliverable:
Create a shortest-path onboarding page for first successful deploy:

- Exact sequence
- Required values only
- Known-good defaults
- Verification checkpoints

Acceptance criteria:

- Can be followed without cross-referencing multiple docs
- New user gets to health endpoint and auth test in one pass

Estimate:

- 0.5 day

## Priority 1: Reliability and Repeatability

### 5. Standardized environment contract

Problem:
Inconsistent naming and variable drift create avoidable failures.

Deliverable:
Define a single contract for:

- Naming conventions
- Required secrets
- Required workflow inputs
- Environment-specific values and ownership

Acceptance criteria:

- Contract is referenced by docs, terraform, and workflows
- Breaking changes require explicit version bump note

Estimate:

- 0.5 day

### 6. Deterministic smoke test workflow

Problem:
Post-deploy confidence depends on manual checks.

Deliverable:
Add automated smoke checks:

- Backend health
- Frontend reachable
- Auth handshake sanity
- CORS sanity

Acceptance criteria:

- Deploy marks success only when smoke checks pass
- Failures indicate which layer broke

Estimate:

- 1 day

### 7. Troubleshooting decision tree

Problem:
Users lose time diagnosing by trial and error.

Deliverable:
Create a symptom-to-fix map for top errors:

- OIDC assume-role failures
- Missing role or provider
- ECR image not found
- App Runner startup failures
- Database URL and driver mismatch
- Clerk token validation mismatch

Acceptance criteria:

- Each symptom has one recommended first action
- Includes commands or checks to confirm resolution

Estimate:

- 0.5 day

## Priority 2: Scale and Velocity

### 8. Template conformance test

Problem:
Changes can regress adoption path silently.

Deliverable:
Add CI checks that validate template readiness:

- Required docs sections present
- Workflow schema and critical steps present
- Terraform module contracts intact

Acceptance criteria:

- CI fails on missing critical template elements
- Runs fast and is mandatory on main

Estimate:

- 1 day

### 9. Multi-environment path normalization

Problem:
Future staging and prod will multiply complexity.

Deliverable:
Define reusable environment matrix:

- Dev, staging, prod conventions
- Shared modules
- Environment overrides strategy

Acceptance criteria:

- Dev to staging promotion is documented and testable
- No copy-paste environment drift

Estimate:

- 1 to 2 days

### 10. Adoption telemetry log

Problem:
No objective data on where adopters spend time.

Deliverable:
Add lightweight setup run log template capturing:

- Start and end time per step
- Failures encountered
- Fix used
- Net time to recover

Acceptance criteria:

- Used on next two adoptions
- Backlog reprioritized from actual friction data

Estimate:

- 0.5 day

## Suggested 7-Day Hardening Sprint

Day 1:

- Preflight command
- Workflow validation hardening

Day 2:

- OIDC bootstrap flow finalization
- Golden path quickstart draft

Day 3:

- Smoke test workflow

Day 4:

- Troubleshooting decision tree
- Environment contract

Day 5:

- Conformance CI checks
- First full dry run from clean clone

Day 6:

- Fix issues from dry run
- Update quickstart and troubleshooting from evidence

Day 7:

- Second dry run by different person
- Freeze vNext and publish release notes

## Definition of Done for Cornerstone vNext

- Fresh adopter can complete provision and deploy in one day or less
- No manual console actions required on normal path
- Bootstrap sequence is deterministic
- Errors fail fast with explicit correction steps
- Documentation supports single-pass setup
- Teardown is proven and repeatable

## Immediate Next Action

Start with Priority 0 items 1 through 3 in the same pull request. Those three changes alone will remove most time-loss patterns you encountered in LockedOnIt.
