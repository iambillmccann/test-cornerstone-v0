This document contains references to Cornerstone

# Architecture Brief

Cornerstone uses a React/Vite frontend and a FastAPI backend.

The backend exposes a REST API documented with OpenAPI.

The database is PostgreSQL. Application persistence uses SQLAlchemy. Migrations use Alembic.

Authentication is outsourced to Clerk. The application database owns app-specific user profile and workspace data.

The system should remain a modular monolith unless a future application clearly requires service separation.
