# Redback Project 4 - Crowd Monitoring and Player Tracking (Project Orion)

Project Orion is a Redback Operations capstone project. It takes AFL match footage and turns it into analytics. Player tracking finds and follows players on the field, and crowd monitoring estimates how many people are in the stands, where they're packed in, and where that could become a safety risk. A web app sits on top so coaches and analysts can upload a video and see the results.

The project carries over from one trimester to the next, so most of the code here was written by earlier students. If you're new, read this page first, then the README in your team's folder.

## How the pieces fit together

```text
Frontend (React)  ->  Backend (FastAPI + PostgreSQL)  ->  Player tracking service
     :8080                    :8000                     ->  Crowd monitoring service
                                                              :8001 / :8002
```

You upload a video in the frontend. The backend saves it, creates a job and sends the video to the player tracking and crowd monitoring services. When they finish, the backend stores the results in PostgreSQL against that job, and the frontend shows them.

During development the backend can return mock results, so you don't need the ML services running to work on the web app.

## Repository structure

```text
redback-orion/
├── backend/                  FastAPI gateway: login and roles, uploads, jobs, results
├── frontend/                 React + Vite web app
├── crowd_monitoring/         Crowd detection, density zones, heatmaps, risk and behaviour analysis
├── player_tracking/
│   ├── player_service/       FastAPI service the backend calls for player analysis
│   ├── player_tracking_logic/  Models and scripts player_service runs (tracking, re-ID,
│   │                           tackle detection, formations), plus earlier experiments
│   └── pipeline/             Training, datasets, tracking quality checks, Forward-50 analysis
├── archive/                  Earlier work, kept for reference (see below)
├── start_all.ps1             Windows script that starts the backend and both services
└── .github/workflows/        Security scan that runs on pull requests
```

Each team works in its own folder: Backend in `backend/`, Frontend in `frontend/`, Crowd Monitoring in `crowd_monitoring/` and Player Tracking in `player_tracking/`. Most folders have a README with more detail.

`archive/` holds work that isn't part of the current app. `archive/26_T1/` is the T1 2026 codebase, and the other folders are projects from before 2026 (IoT, live video dashboard, LLM interfaces and so on). Don't build on it. If you need something from there, copy it into your team's folder in a pull request.

## Running the project

You'll need Python 3.11, Node 20, Docker (for the database) and [uv](https://docs.astral.sh/uv/). Plain `python -m venv` and `pip` work too. Run each part in its own terminal, starting from the repository root.

### 1. Database

The first time:

```bash
docker run -d --name orion-db -p 5432:5432 \
  -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -e POSTGRES_DB=orion_db postgres:16
```

After that, `docker start orion-db` is enough. The backend creates its tables when it starts.

### 2. Backend (port 8000)

```bash
cd backend
uv venv .venv --python 3.11
source .venv/bin/activate          # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
cp .env.example .env
```

In `.env`, set the database line to:

```text
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/orion_db
```

Then start it:

```bash
uvicorn app.main:app --reload --port 8000
```

The API docs are at http://localhost:8000/docs.

### 3. Frontend (port 8080)

```bash
cd frontend
npx pnpm@10.14.0 install
npx pnpm@10.14.0 dev
```

Open http://localhost:8080 and create an account on the login page.

With `USE_MOCK_SERVICES=true` (the default in `.env`), that's the whole app. Uploads go through, but the player and crowd results are fake.

### 4. Real ML results (optional)

Set `USE_MOCK_SERVICES=false` in `backend/.env`, restart the backend, then start both services:

```bash
# Player tracking, port 8001
cd player_tracking/player_service
uv venv .venv --python 3.11 && source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn main:app --port 8001
```

```bash
# Crowd monitoring, port 8002
cd crowd_monitoring
uv venv .venv --python 3.11 && source .venv/bin/activate
uv pip install -r requirements.txt
uvicorn shared.services.main:app --port 8002
```

Both install PyTorch and YOLO, so the first install is slow. If you have an NVIDIA or AMD GPU, the top of `crowd_monitoring/requirements.txt` has the extra install step.

On Windows, `start_all.ps1` starts the backend and both services in one go. You still need to run the database and the frontend yourself.

### Docker Compose

`backend/compose.yaml` builds every service, but the backend container still points at `localhost` for the other services, so it can't reach them yet. Use the steps above until that's fixed.

### Something not working?

- **Port already in use:** another copy is probably still running. Stop it, or change the port.
- **Backend can't connect to the database:** check that `docker ps` shows `orion-db`, and check `DATABASE_URL` in `.env`.
- **The frontend loads but every request fails:** the backend isn't running on port 8000, or the frontend isn't on 8080. The backend only accepts browser requests from ports 8080 and 3000.

## How we work

`main` is the only long-lived branch and the single source of truth. Please don't create trimester folders like `26_T3/`, and don't keep work only in a personal fork.

1. Pull the latest `main` and create a branch named `feature/<team>-<short-description>`, for example `feature/crowd-heatmap-legend`.
2. Keep changes inside your team's folder where you can.
3. Open a pull request into `main`. A stream lead reviews and approves it. GitHub won't let you approve your own pull request.
4. Once it's approved, merge it and delete the branch.

Every pull request also runs an automated security scan.

At the end of each trimester, the final state of `main` is tagged (`v26.T1`, `v26.T2`, and so on). You can check out any tag to see the code exactly as that cohort left it.

## Repository Guidelines

Beginning in the second trimester of 2024, members should follow these guidelines while working with this repository:

- **README.md Files**: All folders should contain a `README.md` (unless the folder is automatically generated, e.g., folders beginning with ".").
- **Naming Conventions**: File and folder names must not contain spaces. Use either snake_case or kebab-case. For instance, instead of "Crowd Monitoring", use "crowd_monitoring" or "crowd-monitoring". Lower-case letters are preferred, but not strictly required.
- **File Organization**: Do not store loose files at the top level of the repository unless explicitly approved.
- **Folder Structure**: Teams should work within a designated subfolder under one of the following top-level directories: Crowd-Monitoring, Player-Tracking, Internet-of-Things, or Others.

  *Update (T3 2026):* the top-level team folders are now `backend/`, `frontend/`, `crowd_monitoring/` and `player_tracking/`. The older Crowd-Monitoring, Player-Tracking, Internet-of-Things and Others work is in `archive/`.

Added in T3 2026:

- Never commit `.env` files with real passwords or keys. Put example values in `.env.example`.
- Large model files (`*.pt`) are ignored by git by default. If the app needs one, add it with `git add -f` and mention it in your pull request.
- Every service has a single `requirements.txt`. Add new Python packages there, not in a new file.

## Where to look next

- `backend/README.md`, plus `API_CONTRACT.md` for the request and response formats
- `crowd_monitoring/README.md` for the crowd pipeline and the JSON schemas
- `player_tracking/pipeline/README.md` and `docs/setup.md` for training and tracking scripts
- Earlier cohorts' handover documents, which the project lead can share
