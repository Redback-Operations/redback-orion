# Frontend Coding Guide (Standards & Workflow)

This guide explains how juniors should code, review, and ship features in this frontend. Follow these standards to keep the codebase consistent, accessible, and easy to maintain.

## Core Principles
- Keep components small, focused, and typed.
- Prefer composition over inheritance; lift shared logic into hooks or utilities.
- No inline styles. Use Tailwind classes or CSS modules when needed.
- Preserve existing design tokens and variables (e.g., `var(--token)`, `@token`, `$token`). Do not rename or replace them.
- Use CSS shorthands (e.g., `p-4`, `px-4`, `m-2`) and keep media queries and breakpoints unchanged.
- Handle errors and loading states explicitly; never swallow errors.

## Folder & Naming Conventions
- Pages: `client/pages/*` (route-level components)
- Components: `client/components/*` (reusable UI and feature blocks)
- UI primitives: `client/components/ui/*` (Radix/Shadcn wrappers)
- Hooks: `client/hooks/*` (prefix with `use`)
- Utilities: `client/lib/*`
- Types: `client/types/*` (cohesive domain-focused typings)
- File names: PascalCase for components/pages, camelCase for hooks/utils, kebab-case for non-TS assets

## React Component Standards
- Use function components with explicit props interfaces.
- Co-locate minimal logic; extract heavy logic to hooks in `client/hooks`.
- Example:
```tsx
import { cn } from "@/lib/utils";

interface PlayerBadgeProps {
  name: string;
  highlight?: boolean;
}

export function PlayerBadge({ name, highlight = false }: PlayerBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded px-2 py-1 text-sm",
        highlight ? "bg-green-600 text-white" : "bg-gray-200 text-gray-900"
      )}
      aria-label={`Player: ${name}`}
    >
      {name}
    </span>
  );
}
```

## Styling & Accessibility
- Tailwind first. Keep existing variables and media queries intact.
- Create descriptive class names when adding CSS classes; avoid generic names like `div-1`.
- Use semantic HTML. Add `aria-*` attributes and keyboard handlers for interactive elements.
- Do not duplicate styles; prefer shared utilities and tokens.

## Data Fetching & State
- Use TanStack Query from `App.tsx` provider.
- Server data: `useQuery`/`useMutation`. Local UI state: `useState`/`useReducer`.
- Example API pattern:
```ts
// client/api/players.ts
import API from "@/api/axiosInstance";
import type { Player } from "@/types/dashboard";

export async function fetchPlayers(): Promise<Player[]> {
  const { data } = await API.get("/players");
  return data;
}
```
```tsx
// inside a component
import { useQuery } from "@tanstack/react-query";
import { fetchPlayers } from "@/api/players";

const { data, isLoading, isError } = useQuery({ queryKey: ["players"], queryFn: fetchPlayers });
```
- 401s trigger a redirect to `/login` via the Axios interceptor.

## Forms & Validation
- Use `react-hook-form` with Zod.
```tsx
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

const schema = z.object({ email: z.string().email(), password: z.string().min(8) });

type FormValues = z.infer<typeof schema>;

export function LoginForm() {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    mode: "onSubmit",
  });

  return (
    <form onSubmit={handleSubmit(() => {})} noValidate>
      <input {...register("email")} aria-invalid={!!errors.email} />
      <input type="password" {...register("password")} aria-invalid={!!errors.password} />
      <button disabled={isSubmitting}>Sign in</button>
    </form>
  );
}
```

## Routing
- Add a page under `client/pages/` and wire it in `client/App.tsx`.
```tsx
// client/pages/MyPage.tsx
export default function MyPage() { return <div className="p-6">Hello</div>; }
```
```tsx
// client/App.tsx
<Route path="/my-page" element={<MyPage />} />
```

## Server Endpoints (Dev & Prod)
- Express routes live in `server/routes/*` and are mounted in `server/index.ts`.
- When adding a new endpoint, define types in `shared/` if shared with client.
- Keep business logic on the server; the client should just call APIs.

## Error Handling
- UI: show explicit error states, never crash silently.
- Network: map server errors to friendly messages. Log details to console only in dev.
- JWT warnings: set `JWT_SECRET` for production to remove the startup warning.

## Testing & Quality
- Vitest for unit tests; co-locate tests as `*.test.ts(x)`.
```ts
import { describe, expect, it } from "vitest";
import { formatNumber } from "@/lib/format";

describe("formatNumber", () => {
  it("formats thousands", () => {
    expect(formatNumber(1200)).toBe("1,200");
  });
});
```
- Run `pnpm typecheck`, `pnpm test`, `pnpm format.fix` before pushing.

## Performance
- Lazy-load large routes/components using `React.lazy` where appropriate.
- Memoize expensive subtrees with `React.memo` and use `useMemo`/`useCallback` intentionally.
- Avoid unnecessary re-renders; keep state as close to where it’s used as possible.

## Security
- Never commit secrets; use environment variables.
- Validate inputs server-side; sanitize any user-facing content.
- Keep dependencies reasonably up to date.

## Git & PR Workflow 
- Small, focused commits with descriptive messages.
- Push via the platform [Push Code] button, then [Create PR]. Keep PRs scoped and linked to an issue.
- Code review checklist:
  - Types correct, no `any` where avoidable
  - No inline styles; tokens preserved; media queries unchanged
  - Loading/error/empty states covered
  - Accessibility: labels, roles, keyboard, focus order
  - Tests and typecheck pass

## Working With Integrations (MCP)
- Connect integrations from the MCP popover:
  - Builder CMS, Linear, Notion, Sentry, Neon, Prisma Postgres, Supabase, Netlify, Zapier, Context7, Figma plugin
- Examples:
  - Error monitoring: [Connect to Sentry](#open-mcp-popover)
  - Deploy hosting: [Connect to Netlify](#open-mcp-popover)
  - DB-backed features: [Connect to Neon](#open-mcp-popover) or [Connect to Supabase](#open-mcp-popover)
  - Docs lookup during dev: [Connect to Context7](#open-mcp-popover)
  - UI from designs: use the Builder.io Figma plugin

## Feature Template (End-to-End)
1. Create types in `client/types` (and `shared/` if used by server).
2. Create API helpers in `client/api/*`.
3. Create components in `client/components/*` and page in `client/pages/*`.
4. Add route in `client/App.tsx`.
5. Style with Tailwind; do not alter existing tokens or breakpoints.
6. Add tests; run `pnpm typecheck`, `pnpm test`, `pnpm format.fix`.
7. Manually verify error/loading/empty states.
8. Push and open PR for review.

Following this guide ensures future contributions remain consistent, maintainable, and production-ready.
