This document contains references to Cornerstone

# Authentication Setup (Clerk)

This guide walks through creating a Clerk app from scratch, wiring local environment variables, and validating login and registration in the frontend.

## Environment Isolation Policy

Cornerstone should not share one Clerk application between local and cloud environments.

Use two Clerk apps:

- `cornerstone-local` for local development only
- `cornerstone-dev` for AWS dev environment only

Reason:

- local Postgres and cloud RDS are different databases
- shared Clerk identities can create cross-environment bootstrap confusion once app users/workspaces are persisted

## 1. Create a Clerk account and application

1. Go to https://dashboard.clerk.com/sign-up.
2. Create your account and verify your email.
3. In the Clerk dashboard, create a new application:
   - Name: `cornerstone-local`
   - Sign-in options: enable `Email + Password`
4. Complete the initial setup wizard.

If cloud dev is in use, create a second application named `cornerstone-dev` with equivalent sign-in options.

## 2. Collect required keys from Clerk

In your Clerk dashboard app:

1. Open API Keys and copy:
   - Publishable key
   - Secret key
2. Open JWT Templates / JWT Settings (or API section) and copy the JWKS URL for your instance.

## 3. Add local environment variables

At repository root, create a local env file from the example if needed:

```bash
cp .env.example .env.local
```

Set these values in `.env.local` for the `cornerstone-local` app:

- `CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `CLERK_JWKS_URL`

Set backend verification values in `apps/api/.env` (copy from `apps/api/.env.example` if needed):

- `CLERK_JWKS_URL` (required)
- `CLERK_ISSUER` (optional, recommended)
- `CLERK_AUDIENCE` (optional)

For Vite frontend runtime, also set in `apps/web/.env.local`:

```bash
VITE_CLERK_PUBLISHABLE_KEY=<your_publishable_key>
VITE_API_BASE_URL=http://localhost:8000
```

Note:

- `VITE_CLERK_PUBLISHABLE_KEY` is the value the React app reads at build/runtime.
- `CLERK_SECRET_KEY` must stay server-side only.

## Cloud Dev Mapping (`cornerstone-dev`)

For AWS `dev`, do not copy local files.

Provide `cornerstone-dev` values through `.github/workflows/provision-dev.yml` inputs:

- `clerk_jwks_url`
- `clerk_issuer` (optional)
- `clerk_audience` (optional)
- `clerk_publishable_key`
- `clerk_secret_key_arn` (Secrets Manager ARN containing dev secret key)

Then deploy with `.github/workflows/deploy-dev.yml`, which reads the publishable key from SSM at deploy time.

## Allowed Origins and Redirect URLs

Set Clerk dashboard URLs per app and do not mix environments.

`cornerstone-local`:

- Allowed origins: localhost variants only (`http://localhost:5173`, etc.)
- Redirect URLs: localhost frontend and local callback paths

`cornerstone-dev`:

- Allowed origins: CloudFront URL only
- Redirect URLs: CloudFront and App Runner URLs for the dev environment

## 4. Start the frontend and test auth

From `apps/web`:

```bash
nvm use 20.19.0
npm install
npm run dev
```

Then validate:

1. Open the app root URL.
2. Confirm signed-out users are redirected to `/sign-in`.
3. Create an account via `/sign-up`.
4. Confirm successful redirect into the app shell.
5. Sign out from the user menu and verify you are redirected to `/sign-in`.

## 5. Troubleshooting

- If the app throws `Missing VITE_CLERK_PUBLISHABLE_KEY`, add the key to `apps/web/.env.local` and restart Vite.
- If sign-in page fails to load, confirm you are using the publishable key (not the secret key) in the Vite variable.
- If session redirects fail, ensure app routes include `/sign-in/*` and `/sign-up/*`.
