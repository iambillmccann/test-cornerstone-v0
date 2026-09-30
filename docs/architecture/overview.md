This document contains references to Cornerstone

# Architecture Overview

Cornerstone uses a modular monorepo structure.

The default architecture is:

- React, TypeScript, and Vite for the frontend
- FastAPI and Python for the backend
- REST and OpenAPI for API contracts
- PostgreSQL for persistence
- SQLAlchemy for ORM
- Alembic for migrations
- Clerk for authentication
- AWS App Runner for API hosting
- AWS RDS (PostgreSQL) for managed database hosting
- AWS S3 + CloudFront for frontend hosting
- Terraform (provider adapter model) for cloud infrastructure
- GitHub Actions for CI/CD validation

Cornerstone is designed as a serverless-friendly modular monolith. Domain boundaries should be clear, but deployment should remain simple until an application justifies additional operational complexity.

Cornerstone's infrastructure is organized using a provider adapter structure under `infra/providers/{provider}`. AWS is implemented today, while additional provider adapters (GCP/Azure) are planned to preserve portability without changing application-layer contracts.
