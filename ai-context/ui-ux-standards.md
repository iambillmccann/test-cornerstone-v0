This document contains references to Cornerstone

# UI/UX Standards — Cornerstone Frontend

## Overview

Cornerstone uses **Tailwind CSS** for styling, **shadcn/ui** for component primitives, and **composition wrappers** for customization safety. This document establishes baseline conventions to keep the frontend maintainable and extensible.

## Component Architecture

### shadcn/ui Component Usage

All UI primitives (buttons, cards, forms, etc.) come from shadcn/ui:

- **Install into source:** Components are copied into `src/components/ui/` (not npm-linked)
- **Never modify ui/ directly:** Treat `src/components/ui/*.tsx` as read-only upstream copies
- **Customize via wrappers:** Create `src/components/*.tsx` wrappers for app-level customizations
- **See:** [0002-frontend.md](../decisions/0002-frontend.md) for detailed pattern

### Component File Layout

```
src/
  components/
    ui/                    # Pristine shadcn copies
      button.tsx
      card.tsx
      dialog.tsx
      ...
    layout/                # Shared layout components (app shell, sidebar, etc.)
      Header.tsx
      Navigation.tsx
      MainContent.tsx
    Button.tsx             # Wrapped shadcn button with app customizations
    Card.tsx               # Wrapped shadcn card with app customizations
    ...                    # Other app-specific components
  hooks/                   # Custom React hooks (API calls, state, etc.)
    useUser.ts
    useFetch.ts
  lib/
    utils.ts               # cn() utility for className merging
    api.ts                 # API service layer
  pages/                   # Page-level components (if using file-based routing)
    Home.tsx
    Settings.tsx
```

### Custom Components

For non-shadcn components:

- Store in `src/components/` or subdirectories (layout/, forms/, etc.)
- Avoid nesting shadcn copies; keep them exclusively in `ui/`
- Document purpose and any design constraints in a comment block

## Design Tokens & Theming

### Tailwind Configuration

- **Base color:** Neutral (white/gray/black)
- **CSS Variables:** Enabled for dynamic theming (`--colors-*` in `tailwind.config.js`)
- **Responsive breakpoints:** Use Tailwind defaults (sm, md, lg, xl, 2xl)
- **Customization:** Extend theme in `tailwind.config.js` only for project-wide needs

### Color Palette

shadcn/ui provides semantic colors via CSS variables:

- `--primary` / `--primary-foreground`
- `--secondary` / `--secondary-foreground`
- `--muted` / `--muted-foreground`
- `--accent` / `--accent-foreground`
- `--destructive` / `--destructive-foreground`
- `--background` / `--foreground`
- `--border`, `--input`, `--ring`

Use these via Tailwind utilities (`bg-primary`, `text-foreground`, `border-border`, etc.) rather than hardcoding hex values.

### Typography

- **Font family:** System stack (ui-sans-serif, system-ui, sans-serif)
- **Font sizes:** Use Tailwind defaults (text-xs, text-sm, text-base, text-lg, text-xl, etc.)
- **Line height:** Tailwind defaults (leading-tight, leading-normal, leading-relaxed)
- **Custom fonts:** Only add if specified by design; document in `src/index.css`

## Responsive Design

- **Mobile-first:** Write styles for mobile first, then override with `sm:`, `md:`, `lg:` prefixes
- **Breakpoints:** Stick to Tailwind defaults unless project needs custom breakpoints
- **Flex/Grid:** Use Tailwind flex/grid utilities; avoid custom media queries

Example:

```tsx
<div className="flex flex-col md:flex-row md:gap-4">
  <aside className="w-full md:w-64">Navigation</aside>
  <main className="flex-1">Content</main>
</div>
```

## Spacing & Sizing

- Use Tailwind spacing scale (p-1, m-2, gap-4, etc.) consistently
- Standard spacing: 4px (1 unit), 8px (2), 16px (4), 24px (6), 32px (8)
- Avoid magic numbers; if you need a custom size, add it to `tailwind.config.js` with a semantic name

## Form Components

- Use shadcn form primitives (Input, Select, Textarea, Checkbox, Radio, etc.)
- Wrap for app-level consistency (styling, validation patterns)
- Form validation: Implement at component level (React Hook Form, Zod, or similar)
- Error messages: Display inline with field-level errors; use `aria-invalid` and `aria-describedby`

## Accessibility (a11y)

Baseline requirements:

- **ARIA attributes:** Use semantic HTML and ARIA roles/labels where needed
- **Color contrast:** Ensure 4.5:1 for normal text, 3:1 for large text (WCAG AA minimum)
- **Keyboard navigation:** All interactive elements must be keyboard accessible (Tab, Enter, Escape)
- **Focus management:** Visible focus indicators on all focusable elements
- **Alt text:** Provide meaningful alt text for images
- **Links vs. buttons:** Use `<a>` for navigation, `<button>` for actions

shadcn/ui components include baseline a11y by default; maintain it in wrappers.

## API Integration

- **Isolation:** Never fetch directly from components; use custom hooks or service layer
- **Location:** Place API calls in `src/hooks/` or `src/lib/api.ts`
- **Pattern:** Custom hooks abstract fetching logic; components receive data via props
- **Ref:** See [api-conventions.md](api-conventions.md) for REST/response format spec

Example:

```tsx
// src/hooks/useUser.ts
export function useUser(id: string) {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(`/api/users/${id}`)
      .then((r) => r.json())
      .then((d) => setData(d.data)) // Unwrap per API conventions
      .catch(setError);
  }, [id]);

  return { data, error, loading: !data && !error };
}

// src/components/UserCard.tsx
function UserCard({ userId }: { userId: string }) {
  const { data: user } = useUser(userId);
  return user ? <div>{user.name}</div> : null;
}
```

## Naming Conventions

- **Component files:** PascalCase (Button.tsx, UserProfile.tsx)
- **Hook files:** camelCase with `use` prefix (useUser.ts, useFetch.ts)
- **Utilities:** camelCase (cn.ts, api.ts)
- **CSS classes:** Keep Tailwind utilities; avoid custom class names when possible

## Dark Mode

- Tailwind dark mode is configured but **not implemented yet** (feature for later iteration)
- When adding dark support:
  - Use `dark:` prefix for dark mode overrides
  - Define dark CSS variables alongside light in `src/index.css`
  - Test with `class="dark"` on html root

## Performance & Best Practices

- **Lazy loading:** Use React.lazy() for route-level code splitting (if routing exists)
- **Memoization:** Use React.memo() sparingly; profile before optimizing
- **Image optimization:** Use web-safe formats (webp); specify width/height on img tags
- **Dependency arrays:** Always specify dependencies in useEffect() and other hooks

## Documentation

- **In-component:** Add JSDoc comments for complex components, especially props and customizations
- **shadcn versions:** Document shadcn component versions in ui/ files (e.g., "Based on shadcn v1.2.3")
- **Customization reasons:** Explain why a component is wrapped and what was customized (date + reason)

## Linting & Type Safety

- **ESLint:** Enabled for React/React Hooks/TypeScript best practices
- **TypeScript:** Strict mode enabled (`noUnusedLocals`, `noUnusedParameters`, `noFallthroughCasesInSwitch`)
- **Type exports:** Always export component prop types for reusability

Example:

```tsx
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
}

export function Button({ variant = "primary", ...props }: ButtonProps) {
  // ...
}
```

## Known Constraints & Future Work

- **Routing:** Not yet implemented; single-page app at / (home)
- **Dark mode:** CSS variables prepared but UI not wired to theme toggle
- **Form validation:** Basic HTML5 validation only; plan for Zod/React Hook Form integration
- **State management:** No global state library yet; consider Redux/Zustand if needed
- **Testing:** No test suite yet; plan for Vitest + React Testing Library later

## References

- [0002-frontend.md](../decisions/0002-frontend.md) — shadcn Component Composition Pattern
- [api-conventions.md](api-conventions.md) — Backend API contract
- [coding-standards.md](coding-standards.md) — General code style guidelines
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [shadcn/ui Docs](https://ui.shadcn.com/docs)
- [React Best Practices](https://react.dev/learn)
