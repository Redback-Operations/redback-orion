# Frontend

The React web app for Project Orion. Coaches and analysts log in here, upload match footage, and view the player tracking and crowd monitoring results that the backend sends back.

It's built with React 18, React Router 6, TypeScript, Vite, TailwindCSS 3 and Radix UI. A small Express server runs inside the Vite dev server for the few things that have to stay server-side. Everything runs on one port, **8080**.

## What's in this folder

```text
frontend/
├── client/            React app
│   ├── pages/         One file per route (Index.tsx is the home page)
│   ├── components/    Shared components; components/ui/ is the Radix-based UI library
│   ├── lib/           Helpers, including config.ts (backend URL)
│   └── App.tsx        Route definitions
├── server/            Express server (routes under server/routes/, served at /api/...)
├── shared/            Types used by both client and server
├── public/            Static files
├── OAUTH_SETUP.md     Google and Apple sign-in setup
└── AGENTS.md          Notes on the starter template's conventions
```

## Setup

You'll need **Node 20** or newer. You don't need to install pnpm globally: the commands below run the exact version pinned in `package.json` through `npx`.

The frontend talks to the backend at `http://localhost:8000`, so for anything beyond looking at the login page you need the database and backend running first. Each of these runs in its own terminal, starting from the repository root.

### 1. Database

The first time:

```bash
docker run -d --name orion-db -p 5432:5432 \
  -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=orion_db postgres:16
```

After that, `docker start orion-db` is enough.

### 2. Backend (port 8000)

```bash
cd backend
uv venv .venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

> [!NOTE]
> **Using Git Bash on Windows?** `source .venv/bin/activate` fails with `No such file or directory`, because on Windows the venv puts its scripts in `Scripts/`, not `bin/`. Use this instead:
>
> ```bash
> source .venv/Scripts/activate
> ```
>
> In PowerShell it's `.venv\Scripts\Activate.ps1`, and in Command Prompt `.venv\Scripts\activate.bat`. If `which python` still points at your system Python afterwards, the venv isn't active.

`backend/.env` has `USE_MOCK_SERVICES=true` by default, so uploads return fake player and crowd results and you don't need the ML services to work on the frontend. See the [root README](../README.md#4-real-ml-results-optional) if you want real results.

### 3. Frontend (port 8080)

```bash
cd frontend
npx pnpm@10.14.0 install
npx pnpm@10.14.0 dev
```

Open http://localhost:8080 and create an account on the login page.

To point the app at a backend somewhere other than `http://localhost:8000`, set `VITE_BACKEND_URL` in `frontend/.env` and restart the dev server. Google and Apple sign-in need extra setup, covered in [OAUTH_SETUP.md](OAUTH_SETUP.md).

### Other commands

```bash
npx pnpm@10.14.0 build       # production build into dist/
npx pnpm@10.14.0 start       # run the production build
npx pnpm@10.14.0 typecheck   # TypeScript check
npx pnpm@10.14.0 test        # Vitest tests
```

## Known limitation: demo data

Several pages still show hardcoded or randomly generated numbers instead of real results. These include the Live Match and Crowd Monitor tabs on the dashboard, the CrowdMonitor zones, the report downloads and the API Diagnostics page. [DUMMY_DATA_AUDIT.md](DUMMY_DATA_AUDIT.md) lists every one as a checklist. Tick items off there as you replace them.

## Don't use the Docker Compose stack yet

> [!WARNING]
> `backend/compose.yaml` builds the frontend along with the backend, database and ML services, but **it doesn't give you a working app yet**. Use the steps above instead.
>
> - Inside the backend container, the player and crowd service URLs still point at `localhost`, which is the container itself, so the backend can't reach them.
> - Compose publishes ports 8080, 8000, 8081, 8002 and 5432. If it's running, or was left running, your local dev servers and the `orion-db` container can't bind those ports. Run `docker compose down` in `backend/` before going back to the local setup.

## Something not working?

- **The page loads but every request fails:** the backend isn't running on port 8000. Check that http://localhost:8000/docs loads.
- **Requests are blocked by CORS:** the backend only accepts browser requests from ports 8080 and 3000. If something else was already on 8080, Vite quietly starts on 8081 instead (check the URL it prints). Stop whatever is on 8080 (often a leftover Compose stack) and restart the dev server.
- **Changes to `.env` don't show up:** Vite only reads `.env` at startup, so restart the dev server.

## Adding a page

1. Create the component in `client/pages/MyPage.tsx`.
2. Add a route in `client/App.tsx`, above the catch-all `*` route:

   ```tsx
   <Route path="/my-page" element={<MyPage />} />
   ```

Only add an Express endpoint under `server/routes/` when something really has to run server-side, such as handling a private key. Everything else should go through the FastAPI backend.
