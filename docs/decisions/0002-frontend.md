This document contains references to Cornerstone

# 0002: shadcn/ui Component Composition Pattern

## Decision

Cornerstone uses shadcn/ui components via **composition wrapper pattern** to isolate customizations and protect against breaking changes during upstream updates.

## Pattern

**Directory structure:**

```
src/
  components/
    ui/              # Pristine shadcn/ui copies (do not modify)
      button.tsx
      card.tsx
      ...
    Button.tsx       # App-level wrapper with customizations
    Card.tsx         # App-level wrapper with customizations
    ...
```

**Composition example:**

```tsx
// src/components/ui/button.tsx — From shadcn (untouched)
export { Button } from "@radix-ui/react-primitive";

// src/components/Button.tsx — Our wrapper
import {
  Button as ShadcnButton,
  type ButtonProps,
} from "@/components/ui/button";

/**
 * App Button component
 * Based on shadcn button v1.2.3 (2026-05)
 *
 * Customizations:
 * - Added disabled-state opacity per design spec
 */
export function Button(props: ButtonProps) {
  return (
    <ShadcnButton
      className={`${props.className} disabled:opacity-60`}
      {...props}
    />
  );
}
```

**Usage in app:**

```tsx
import { Button } from "@/components/Button"; // Use wrapper, not ui/Button

export function Header() {
  return <Button variant="primary">Click me</Button>;
}
```

## Rationale

- **Isolation:** App customizations are separate from upstream changes
- **Maintainability:** Running `npx shadcn@latest add button --reinstall` only touches `ui/button.tsx`; wrappers absorb breaking changes via git diff review
- **Clarity:** Easy to distinguish what's custom vs. original
- **Safety:** Single point of adaptation if shadcn API changes

## Update Workflow

When a shadcn component needs updating:

1. **Reinstall from registry:**

   ```bash
   npx shadcn@latest add button --reinstall
   ```

2. **Review git diff** for breaking changes in `ui/button.tsx`

3. **Test and adapt wrapper** if needed (e.g., new props, removed exports)

4. **Commit separately** so updates are traceable

## Documentation

- Add comment at top of `src/components/ui/*.tsx` showing shadcn version when added
- Document all customizations in wrapper (`src/components/*.tsx`) with date and reason
- Keep a simple changelog entry for significant updates

## Scope

This pattern applies to all shadcn/ui components in the project. For custom components not from shadcn, use standard React patterns without the wrapper layer.

## Notes

This design honors shadcn's philosophy of "copy-paste library" while adding maintainability guardrails appropriate for a reusable template.

## 2026-06-05 Addendum: Cornerstone-Owned Auth UI with Clerk Infrastructure

### Decision

Cornerstone uses Clerk for identity/session infrastructure but owns the user-facing auth/account UX through Cornerstone-native pages and shell controls.

### Adopted Route Pattern

- Public routes:
  - `/sign-in`
  - `/sign-up`
- Protected routes:
  - `/`
  - `/settings`
  - `/settings/account`

### What Changed

- Replaced Clerk prebuilt auth components in normal flow (`<SignIn />`, `<SignUp />`, `<UserButton />`) with custom Cornerstone UI.
- Implemented custom sign-in/sign-up forms using Clerk React hooks and session activation APIs.
- Added Cornerstone-styled account page at `/settings/account` showing Clerk identity basics and sign-out.
- Kept existing protected layout behavior and redirects.

### Boundaries and Constraints

- Clerk remains the authentication provider and session authority.
- Backend `/api/me` remains canonical for application user/profile/workspace context.
- App-specific state stays separate from Clerk identity state.
- No custom password storage or provider replacement.
- No cloud/deployment changes in this phase.

### Rationale

- Removes external vendor-branded auth surfaces from primary product UX.
- Preserves mature Clerk identity/session infrastructure and backend JWT validation contract.
- Keeps Cornerstone reusable and branding-neutral while minimizing auth/security risk.

### Scope Limits for This Iteration

- Email/password auth UI only.
- Account page is intentionally lightweight: identity display + sign-out.
- Advanced account security management (MFA factors, passkeys, complex verification UX) remains a follow-up phase unless tenant policy requires immediate support.

### 2026-06-05 Follow-up: Required Sign-up Verification Handling

#### Decision

Custom sign-up UX must include a verification continuation step when Clerk requires email verification, and must include password confirmation before initial sign-up submit.

#### Why

- Some Clerk tenant configurations do not complete sign-up immediately after email/password create.
- Without continuation handling, users encounter a terminal error state and cannot activate accounts.
- Password confirmation is a baseline UX safeguard for reusable templates.

#### Resulting pattern

- Step 1: collect email, password, and confirm password.
- Step 2: on non-complete sign-up status, prepare email verification code and render code-entry form.
- Step 3: verify code and activate Clerk session.

### 2026-06-05 Follow-up: Fresh token + single retry for app-context bootstrap

#### Decision

When loading app context via `/api/me`, frontend requests a fresh Clerk token (`skipCache`) and retries once on bearer-token 401 errors.

#### Why

- Post-auth transitions can briefly race token cache/session activation state.
- A single bounded retry improves user experience without hiding persistent auth issues.

#### Boundaries

- Retry is limited to one attempt.
- This does not change backend verification policy or Clerk provider ownership.

### 2026-06-05 Follow-up: OAuth providers in custom auth UI

#### Decision

Cornerstone auth pages include first-party OAuth provider actions for Google, Apple, and Microsoft using Clerk redirect APIs.

#### Route/flow

- Auth pages trigger Clerk `authenticateWithRedirect`.
- Clerk returns to `/sso-callback`.
- Callback finalizes session and redirects to `/`.

#### Constraints

- Providers are shown in UI as product defaults for reusable template UX.
- Successful auth still depends on provider enablement/configuration in Clerk Dashboard.

### 2026-06-05 Follow-up: Cross-provider/session transition resilience

#### Decision

Adopt bounded frontend retry and backend clock-skew tolerance to reduce transient token-validation failures during auth method/account transitions.

#### Policy

- `/api/me` bootstrap call retries once on HTTP 401 auth responses.
- Retry includes a short delay to allow session/token propagation.
- Backend Clerk JWT decode applies a small leeway window.

#### Guardrails

- Retry remains single-attempt to avoid masking persistent auth misconfiguration.
- API response contract remains unchanged (`Invalid or expired bearer token` for 401 decode failures).

### 2026-06-05 Follow-up: Theme initialization scope

#### Decision

`useTheme()` is called in the root `App` component so the system/saved theme preference is applied to all routes, including public auth pages.

#### Why

The hook was previously only invoked inside `Layout`, which is only rendered for protected routes. Public pages rendered without theme initialization and always appeared in light mode.

#### Rule

Any hook that must affect the global document (theme class, locale, etc.) belongs at the `App` root, not inside layout wrappers scoped to a subset of routes.
