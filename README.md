# Redback Project 4 - Crowd Monitoring and Player Tracking (Project Orion)

Project Orion is a Redback Operations capstone project. It takes AFL match footage and turns it into analytics. Player tracking finds and follows players on the field, and crowd monitoring estimates how many people are in the stands, where they're packed in, and where that could become a safety risk. A web app sits on top so coaches and analysts can upload a video and see the results.

The project carries over from one trimester to the next, so most of the code here was written by earlier students. If you're new, read this page first, then the README in your team's folder.

## Repository guidelines

These rules have applied since T2 2024 and were updated in T3 2026. Please follow them in every pull request.

- **Work in your team's folder.** Backend, Frontend, Crowd Monitoring and Player Tracking each have a top-level folder (see [Repository structure](#repository-structure)). Don't add loose files at the top level of the repo unless the project lead agrees.
- **Give every folder a `README.md`** that says what's in it and how to run it. Generated folders and folders starting with `.` are the exception.
- **No spaces in file or folder names.** Use snake_case or kebab-case, so `crowd_monitoring` or `crowd-monitoring` rather than `Crowd Monitoring`. Lower case is preferred.
- **Go through `main`.** Work happens on feature branches merged into `main` by pull request (see [Branching strategy](#branching-strategy-github-flow)). Don't create trimester folders like `26_T3/`, and don't keep work only in a personal fork.
- **Keep secrets out of git.** Never commit `.env` files with real passwords or keys. Put example values in `.env.example`.
- **Add large model files on purpose.** Git ignores `*.pt` files by default. If the app needs one, add it with `git add -f` and mention it in your pull request.
- **One `requirements.txt` per service.** Add new Python packages to the service's existing file instead of creating another one.

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

## Branching strategy (GitHub flow)

We use GitHub flow: short-lived feature branches, merged into `main` through pull requests.

```text
main  ──●────────●────────●────────●──  (tag v26.T3 at handover)
         \      /  \      /
          feature/...    feature/...
```

`main` is the only long-lived branch and the single source of truth. There are no release or trimester branches.

1. Start from the latest `main`:

   ```bash
   git switch main
   git pull
   git switch -c feature/<team>-<short-description>   # e.g. feature/crowd-heatmap-legend
   ```

2. Commit your work, keeping changes inside your team's folder where you can. Push the branch and open a pull request into `main`:

   ```bash
   git push -u origin feature/<team>-<short-description>
   gh pr create --base main
   ```

3. A stream lead reviews and approves it. GitHub won't let you approve your own pull request, and every pull request also runs an automated security scan.
4. Once it's approved, merge it and delete the branch. If `main` has moved on while you were working, run `git pull origin main` on your branch first and fix any conflicts.

Try to keep branches small and merge them within a sprint. The longer a branch lives, the harder it is to merge.

Each trimester's final state is kept as a tag on `main` (`v26.T1`, `v26.T2`, and so on). To see the code exactly as a cohort left it, run `git switch --detach v26.T2`.

## Steps before handover

At the end of each trimester, the project lead (or whoever has Maintain access) does the following, so the next team starts from a clean repo where everything is in `main`.

**1. Merge or close every open pull request.** When you're done, nothing should be left pending.

```bash
gh pr list --state open
```

For each one, either get it reviewed and merged, or close it with a comment explaining why. Work that won't be finished can still be kept: close the PR and tag its branch (see step 2).

**2. Delete feature branches that are merged, stale or no longer useful.** Only `main` should remain.

```bash
git fetch --prune
git branch -r --merged origin/main | grep -v 'origin/main'     # already in main, safe to delete
git branch -r --no-merged origin/main                          # not in main, check these first
```

Delete a branch that's already merged:

```bash
git push origin --delete <branch-name>
```

If a branch has work that isn't in `main` but might be useful later, tag it before deleting it, so nothing is lost:

```bash
git tag -a archive/<branch-name> origin/<branch-name> -m "Unmerged work from <branch-name>, T3 2026"
git push origin archive/<branch-name>
git push origin --delete <branch-name>
```

**3. Tag the trimester on `main`.** Use `v<year>.T<trimester>`, for example `v26.T3`:

```bash
git switch main
git pull
git tag -a v26.T3 -m "End of T3 2026"
git push origin v26.T3
```

**4. Final check.** All three should come back clean:

```bash
gh pr list --state open                # no open pull requests
git ls-remote --heads origin           # only refs/heads/main
git ls-remote --tags origin | grep v26.T3
```

The repo is then ready to hand over to the next team. Update this README and the handover documents if anything about running the project has changed.

## Where to look next

- `backend/README.md`, plus `API_CONTRACT.md` for the request and response formats
- `crowd_monitoring/README.md` for the crowd pipeline and the JSON schemas
- `player_tracking/pipeline/README.md` and `docs/setup.md` for training and tracking scripts
- Earlier cohorts' handover documents, which the project lead can share
