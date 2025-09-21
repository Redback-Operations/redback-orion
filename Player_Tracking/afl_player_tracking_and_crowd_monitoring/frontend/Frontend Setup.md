# Frontend Setup and Onboarding Guide

This guide explains how to set up, run, understand, and extend the AFL Player Tracking & Crowd Monitoring frontend. It is designed for  future maintainers.

- Tech: React 18, TypeScript, Vite 7, TailwindCSS 3, Radix UI, Express (integrated for APIs in dev and prod), TanStack Query, Vitest
- App location: `Player_Tracking/afl_player_tracking_and_crowd_monitoring/frontend`
- Dev port: 8080

## 1) Prerequisites
- Node.js 18+ (22+ recommended)
- npm (bundled with Node.js)
- Git access to the repository

## 2) Install and Run (Local) with npm
From the frontend folder:

```bash
cd Player_Tracking/afl_player_tracking_and_crowd_monitoring/frontend
npm install
npm run dev
```

- Local dev server: http://localhost:8080/
- Vite serves the SPA; Express is attached as middleware so API routes are available at `/api/*` in development.

Note: This repository also contains a `pnpm-lock.yaml`. Using npm will ignore that file. If your environment warns about mixed lockfiles, you can safely proceed with npm, or remove the pnpm lockfile in your local clone.

### Production build and run
```bash
npm run build       # builds client to dist/spa and server to dist/server
npm start           # serves dist via Express (node dist/server/node-build.mjs)
```
- Production server reads `process.env.PORT` (defaults 3000).

### Useful scripts
- `npm test` – run Vitest tests
- `npm run typecheck` – TypeScript type checking
- `npm run format.fix` – format code with Prettier

## 3) Environment Variables
Environment variables are consumed in the Express server.

Common variables:
- `JWT_SECRET` – Required for production auth token signing
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` – For Google OAuth
- `APPLE_CLIENT_ID`, `APPLE_TEAM_ID`, `APPLE_KEY_ID`, `APPLE_PRIVATE_KEY` – For Apple Sign In
- `CLIENT_URL` – Client origin (default `http://localhost:8080`)
- `PING_MESSAGE` – Overrides `/api/ping` message
- `PORT` – Production server port

Local development (.env):
```bash
# file: Player_Tracking/afl_player_tracking_and_crowd_monitoring/frontend/.env
JWT_SECRET=your-local-dev-secret
CLIENT_URL=http://localhost:8080
PING_MESSAGE=ping
# OAuth (optional for local testing)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
APPLE_CLIENT_ID=
APPLE_TEAM_ID=
APPLE_KEY_ID=
APPLE_PRIVATE_KEY=
```
Do not commit real secrets. Use environment variables locally via a `.env` file and configure secrets in your deployment environment.

OAuth details are documented in `OAUTH_SETUP.md`.

## 4) Project Structure (Frontend)
```
frontend/
├─ client/               # React SPA
│  ├─ pages/             # Route components (Index.tsx = sample route)
│  ├─ components/        # UI and feature components
│  │  ├─ auth/           # Auth screens & helpers
│  │  └─ ui/             # Shadcn/Radix UI wrappers
│  ├─ api/               # Axios instance and API helpers
│  ├─ hooks/             # Custom hooks
│  ├─ lib/               # Utilities, formatting, mocks, reports
│  ├─ types/             # Shared TS types for client
│  ├─ App.tsx            # Router setup
│  └─ global.css         # Tailwind styles
├─ server/               # Express server (used in dev & prod)
│  ├─ routes/            # API handlers (oauth.ts, demo.ts)
│  ├─ index.ts           # createServer() wiring
│  └─ node-build.ts      # Serves built SPA in prod
├─ shared/               # Shared types (client & server)
├─ public/               # Static assets
├─ vite.config.ts        # Vite + Express dev-integration
├─ vite.config.server.ts # Server build config
└─ package.json
```

Key files to know:
- `client/App.tsx` – routes (react-router-dom)
- `client/api/axiosInstance.ts` – preconfigured Axios with token handling
- `server/index.ts` – Express app, mounts `/api/*`
- `server/routes/oauth.ts` – Google/Apple auth flows and JWT

## 5) Routing and Pages
Routes live in `client/pages/` and are wired in `client/App.tsx`:
- `/` or `/login` – Login page (`client/pages/Login.tsx`)
- `/home`, `/afl-dashboard` – Main dashboard
- `/player-performance`, `/team-match-performance` – Analytics pages
- `/crowd-monitor`, `/analytics`, `/reports`, `/api-diagnostics`, `/error-demo`, `/stitch`
- Fallback route `*` -> NotFound

Add a new page:
1) Create `client/pages/MyPage.tsx`
2) Add route in `client/App.tsx`:
```tsx
<Route path="/my-page" element={<MyPage/>} />
```

## 6) UI and Styling
- TailwindCSS 3 utilities with theme tokens in `client/global.css`
- Radix UI components wrapped in `client/components/ui/*`
- Keep existing design tokens/variables intact
- Prefer class names over inline styles; create small, descriptive class names

## 7) State, Data Fetching, and APIs
- TanStack Query (`QueryClientProvider` in `App.tsx`) handles caching/retries
- Axios instance: `client/api/axiosInstance.ts`
  - Base URL defaults to `http://127.0.0.1:8000/api/v1`
  - If your backend differs, update `baseURL` accordingly
  - Automatically attaches `Authorization: Bearer <token>` from `localStorage`
  - 401 responses clear token and redirect to `/login`

Calling APIs:
```ts
import API from "@/api/axiosInstance";
const { data } = await API.get("/players");
```

## 8) Authentication
- OAuth endpoints are exposed via Express server (`server/routes/oauth.ts`):
  - `GET /api/auth/google`, `GET /api/auth/google/callback`
  - `POST /api/auth/apple/callback`
  - `POST /api/auth/verify-token`
- Requires `JWT_SECRET` in production; defaults to a dev-only secret and logs a warning otherwise
- See `OAUTH_SETUP.md` for complete setup

## 9) Testing and Quality
- Unit tests: `npm test` (Vitest)
- Types: `npm run typecheck`
- Formatting: `npm run format.fix`

Suggested conventions:
- Keep components small and cohesive
- Co-locate tests next to components when practical
- Prefer descriptive names (e.g., `PlayerStatsGrid`) over generic ones
- Avoid TODO/placeholder comments; implement real logic

## 10) Build and Deploy
- `npm run build` outputs:
  - SPA: `dist/spa`
  - Server: `dist/server/node-build.mjs`
- `npm start` serves both via Express

Deployment options:
- Host on any Node-capable environment or platform. Configure environment variables in that environment and run `npm start`.

## 11) Troubleshooting (Common Issues)
- Install fails at repo root: run commands inside `frontend/` (this app’s package.json lives here)
- Mixed lockfile warnings: npm ignores `pnpm-lock.yaml`; proceed with npm or remove that file locally
- Warning: `Using default JWT_SECRET` – set `JWT_SECRET` before production
- 401s from API: token expired or invalid; the app will redirect to `/login`
- Wrong API URL: update `client/api/axiosInstance.ts` `baseURL` to your backend
- Port conflicts: change Vite dev port in `vite.config.ts` (server.port)

## 12) How to Add a Feature (Example Flow)
1) Plan UI and data needs
2) Create a page/component under `client/pages` or `client/components`
3) Add the route in `client/App.tsx`
4) Use `API` for data fetching; model response types in `client/types`
5) Style with Tailwind and UI components under `client/components/ui`
6) Add basic tests (Vitest) if applicable
7) Run `npm run typecheck`, `npm test`, `npm run format.fix`
8) Verify locally (`npm run dev`), then build (`npm run build`) if needed

## 13) Useful Endpoints (Dev)
- `GET /api/ping` – returns `{ message: PING_MESSAGE || "ping" }`
- `GET /api/demo` – example endpoint

## 14) Security Best Practices
- Never commit secrets; use environment variables
- Rotate `JWT_SECRET` regularly and use strong values
- Validate inputs on server endpoints
- Keep dependencies updated (check for warnings)

## 15) References
- `AGENTS.md` – fusion starter overview
- `OAUTH_SETUP.md` – detailed OAuth configuration
- `client/App.tsx` – route definitions
- `server/index.ts` – Express API wiring
- `client/api/axiosInstance.ts` – Axios configuration

With this, a new team member should be able to install, run, navigate the code, and implement new features safely and consistently.
