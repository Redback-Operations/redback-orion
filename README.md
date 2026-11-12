# Redback Project 4 (Orion): Player Tracking and Crowd Monitoring

`main` is the single source of truth. There are no per-trimester folders; each trimester's final state is a git tag (`v26.T1`, `v26.T2`, ...).

## Layout

| Folder | What | Run |
|--------|------|-----|
| `backend/` | FastAPI gateway: auth, uploads, jobs, PostgreSQL (port 8000) | `pip install -r requirements.txt`, copy `.env.example` to `.env`, `uvicorn app.main:app --reload` |
| `frontend/` | React + Vite web app | `pnpm install`, `pnpm dev` |
| `crowd_monitoring/` | Crowd detection, density, heatmaps service (port 8002) | `pip install -r requirements.txt`, `uvicorn shared.services.main:app --port 8002` |
| `player_tracking/player_service/` | Player tracking API (port 8080) | `pip install -r requirements.txt`, `uvicorn main:app --port 8080` |
| `player_tracking/player_tracking_logic/` | Tracking, re-ID and tackle models used by `player_service` | Keep next to `player_service/` |
| `player_tracking/pipeline/` | Training, datasets, Forward-50 analysis | See its `README.md` |
| `archive/` | Earlier work (26_T1, pre-2026 folders). Read-only | |

`start_all.ps1` (Windows) starts the backend and both services. With `USE_MOCK_SERVICES=true` in `backend/.env`, the backend returns mock results, so only `backend/` and `frontend/` are needed.

Docker: `cd backend && docker compose up --build`.

## Workflow

- Branch from `main`: `feature/<team>-<short-name>`.
- Open a PR into `main`; a stream lead reviews and approves. You cannot approve your own PR.
- Work in your team's folder. Do not create trimester folders or keep work only in a fork.
- File and folder names: no spaces; snake_case preferred.
