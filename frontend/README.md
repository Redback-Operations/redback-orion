# Frontend

The React web app for Project Orion. Coaches and analysts log in here, upload match footage, and view the player tracking and crowd monitoring results that the backend sends back.

It's built with React 18, React Router 6, TypeScript, Vite, TailwindCSS 3 and Radix UI. Vitest and the React testing library are used for automated frontend testing. A small Express server runs inside the Vite dev server for the few things that have to stay server-side. Everything runs on one port, **8080**.

## What's in this folder

```text
frontend/
├── client/            React app
│   ├── pages/         One file per route (Index.tsx is the home page)
│   ├── components/    Shared components; components/ui/ is the Radix-based UI library
│   ├── lib/           Helpers, including config.ts (backend URL)
|   ├──tests/          Automated frontend tests
│   │   ├── unit/      Tests for individual functions and application logic
│   │   ├── components/ Tests for React components and user interactions
│   │   └── setup.ts   Shared test environment setup
│   └── App.tsx        Route definitions
├── server/            Express server (routes under server/routes/, served at /api/...)
├── shared/            Types used by both client and server
├── public/            Static files
├── vitest.config.ts   Frontend testing configuration
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

To point the app at a backend somewhere other than `http://localhost:8000`, set `VITE_BACKEND_URL` in `frontend/.env` and restart the dev server.

**Working on player screens with an empty database?** Create `frontend/.env.local` containing `VITE_USE_MOCK_PLAYERS=true` and restart the dev server. Player Performance and the dashboard's Player Performance tab then show the example players from `client/lib/mockPlayers.ts`, with a yellow banner saying so. `.env.local` is gitignored, so this only affects your machine, and production builds ignore the setting. Google and Apple sign-in need extra setup, covered in [OAUTH_SETUP.md](OAUTH_SETUP.md).

### Other commands

```bash
npx pnpm@10.14.0 build       # production build into dist/
npx pnpm@10.14.0 start       # run the production build
npx pnpm@10.14.0 typecheck   # TypeScript check
npx pnpm@10.14.0 test        # Vitest tests
npx pnpm@10.14.0 test:watch     # rerun tests when files change
npx pnpm@10.14.0 test:coverage  # run tests and generate coverage report
```
## Frontend testing

The frontend uses [Vitest](https://vitest.dev/guide/) and [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) for automated testing. Tests run in a simulated browser environment using jsdom, so the backend database and mock services don't need to be running for isolated frontend tests.

### Running tests

From the `frontend/` directory:

```bash
npx pnpm@10.14.0 install
npx pnpm@10.14.0 test
```

To automatically rerun tests when files change:

```bash
npx pnpm@10.14.0 test:watch
```

### Adding tests

Tests are located in `client/tests/` and are separated into the following folders:

- unit/ - these are tests for individual functions and application logic.
- components/ - these are tests for React components, rendering and user interactions.

Use ".test.ts" for TypeScript unit tests and ".test.tsx" for React component tests.

The test environment is configured in `vitest.config.ts`, with shared setup in `client/tests/setup.ts`. The existing `@/` and `@shared/` path aliases can also be used in test files.

please use mock external API requests where possible so that tests can run independently of the backend.

### Code coverage

To generate a code coverage report:

```bash
npx pnpm@10.14.0 test:coverage
```

Coverage reports are generated in `coverage/`. Open `coverage/index.html` in your browser to view the percentage of statements, branches, functions and lines covered by the tests.

The coverage/ directory is generated locally and should not be committed to Git. make sure it is included in your 
gitignore file

### Continuous integration

Frontend tests are automatically run through GitHub Actions using `.github/workflows/frontend-tests.yml` at the repository root.

security checks on python security vulnerabilities and dependencies are done through a security-scan.yml file which also runs seperate to our frontend tests

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
