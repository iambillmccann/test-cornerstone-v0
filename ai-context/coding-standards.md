# Coding Standards

General standards:

- Prefer boring, explicit code.
- Keep domain logic out of route handlers.
- Keep API schemas separate from database models.
- Use clear names over clever abstractions.
- Add tests for reusable behavior.
- Avoid speculative generalization.

Python standards:

- Use type hints.
- Use Pydantic for API request and response schemas.
- Use SQLAlchemy for persistence models.
- Use service modules for business logic.

Frontend standards:

- Use React with TypeScript.
- Use functional components.
- Use shared layout components.
- Keep API access isolated from UI components.
