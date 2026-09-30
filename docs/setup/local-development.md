# Local Development

Local development should run with:

- frontend dev server
- backend API server
- local PostgreSQL container

The local PostgreSQL instance is managed through Docker Compose.

Start the database:

```bash
./scripts/dev-db-up.sh
```

Stop the database:

```bash
./scripts/dev-db-down.sh
```

Reset the database:

```bash
./scripts/dev-db-reset.sh
```

Authentication setup:

- Follow [Authentication Setup (Clerk)](./authentication.md) before running login and registration flows locally.
