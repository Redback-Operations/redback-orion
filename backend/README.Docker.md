# Orion Backend Docker Setup

This document explains how to run the Orion project using Docker.

## Requirements

Before starting, make sure the following are installed:

- Docker Desktop
- Git

Docker Desktop must be running before using Docker commands.

## Services

The Docker environment includes:

- Backend API
- Frontend
- PostgreSQL database
- Player tracking service
- Crowd monitoring service

## Main Ports

```text
Backend API:       8000
Frontend:          8080
PostgreSQL:        5432
Crowd Monitoring:  8002
Player Service:    8081 (host) / 8080 (container)
```

Other service ports may depend on the current project configuration.

## Environment Configuration

Docker environment settings are stored in:

```text
.env.docker
```

An example environment configuration is available in:

```text
.env.example
```

Do not commit passwords, API keys, or other sensitive information to GitHub.

### Environment Variables (Docker)

| Variable | Set in | Current value or default | Notes |
| --- | --- | --- | --- |
| `PLAYER_SERVICE_URL` | `.env.docker` | `http://player-tracking:8080` | Internal Docker network name, container port |
| `CROWD_SERVICE_URL` | `.env.docker` | `http://crowd-monitoring:8002` | Internal Docker network name |
| `DATABASE_URL` | `.env.docker` and `compose.yaml` | `postgresql+asyncpg://user:password@db:5432/orion_db` | Defined in both places; the value in `compose.yaml` takes precedence |
| `JWT_SECRET_KEY` | `.env.docker` | `your-secret-key-here` | Placeholder value; replace before real use |
| `PASSWORD_RESET_SECRET` | `.env.docker` | `your-password-reset-secret-here` | Required. The backend exits at startup if it is missing. Placeholder only; `.env.docker` is tracked in git, so replace it with a real value from a non-committed source before real use |
| `UPLOAD_DIR` | `.env.docker` | `uploads` | Path inside the backend container, on the shared uploads volume |
| `USE_MOCK_*` | `.env.docker` | `false` | Uses real services when `false` |
| `DEBUG` | `.env.docker` | `true` | |
| `LOG_LEVEL` | `.env.docker` | `INFO` | |

### Folders Required by Bind Mounts

These folders are referenced by `compose.yaml` but were not present in the clone used for verification. Create them before starting the stack if a service fails to write output:

```text
player_tracking/player_service/outputs
player_tracking/player_service/uploads
crowd_monitoring/output
backend/uploads
```

`crowd_monitoring/analytics_output` exists in the repository.

## Start the Project

Make sure Docker Desktop is running.

From the `backend` directory (the directory containing `compose.yaml`), run:

```bash
docker compose up --build -d
```

Docker will build the required images and start the services.

As verified, this command produces a working backend from the current repository state. Known issue 3 (duplicate `DATABASE_URL`) is still open. See [Known Issues](#known-issues).

If the first build stalls during package installation, stop it and build services one at a time:

```bash
docker compose build backend
docker compose build crowd-monitoring
docker compose build player-tracking
docker compose build frontend
docker compose up -d
```

Note: `--progress` is only accepted by `docker compose build`. It is not a valid flag for `docker compose up` in Docker Compose v5.2.0.

## Run in the Background

To run the containers in the background:

```bash
docker compose up -d
```

## Stop the Project

To stop the containers:

```bash
docker compose down
```

`docker compose down` keeps the named volumes `backend_postgres_data` (database) and `backend_uploads_data` (uploads). Data persists across restarts; this was verified by checking the database tables after `down` and `up -d`.

WARNING: `docker compose down -v` also deletes both volumes, including all database data and uploaded files. Use it only for a full reset.

## Rebuild

If backend dependencies or Docker configuration have changed, rebuild with:

```bash
docker compose up --build
```

## View Running Containers

```bash
docker ps
```

## View Logs

To view Docker Compose logs:

```bash
docker compose logs
```

To continuously follow the logs:

```bash
docker compose logs -f
```

## Backend API

Once the backend is running, it can be accessed at:

```text
http://localhost:8000
```

FastAPI documentation is available at:

```text
http://localhost:8000/docs
```

## Database

The backend uses PostgreSQL.

When running through Docker Compose, the backend should connect to the database using the database service name rather than `localhost`.

For example:

```text
postgresql+asyncpg://user:password@db:5432/orion_db
```

Actual credentials should be provided through the project's environment configuration rather than being hard-coded into application code.

## Troubleshooting

If Docker does not start, first check that Docker Desktop is running.

If containers fail to start, check:

```bash
docker compose logs
```

If changes are not appearing after modifying dependencies or Docker configuration, rebuild:

```bash
docker compose down
docker compose up --build -d
```

## Verified Results

Checked on Windows with Docker Desktop 29.6.1 and Docker Compose v5.2.0.

| Check | Result |
| --- | --- |
| `docker compose config --quiet` | Passed |
| Images build (backend, crowd-monitoring, player-tracking, frontend) | Passed |
| Five containers start | Passed |
| Frontend `http://localhost:8080` | 200 |
| Player service `http://localhost:8081/docs` | 200 (`/health` returns 404) |
| Backend `http://localhost:8000/docs` | 200 |
| Backend `http://localhost:8000/health` | 200, `{"gateway":"ok","player_service":"ok","crowd_service":"ok"}` |
| Backend to `db`, `player-tracking`, `crowd-monitoring` DNS | Passed |
| Database tables created (`jobs`, `players`, `refresh_tokens`, `users`) | Passed |
| Database tables persist after `docker compose down` and `up -d` | Passed |
| Shared uploads volume: backend writes, crowd container reads | Passed |
| Crowd container opens a 1.23 MB sample `.mp4` with OpenCV (171 frames, 24.46 fps) | Passed |
| Crowd service OpenAPI (`/openapi.json`) served from inside the container | Passed |
| Crowd service `/docs` and `/health` | 404 (crowd has no `/docs` or `/health` route; the UI is at `/demo`) |
| `POST /process-crowd-detection` end to end | Not tested |
| Player-to-backend upload and result pipeline end to end | Not tested |
| Second-person test (team member, independent run) | Not done (out of scope for this check) |

The backend results above were obtained from a clean rebuild after fixes for known issues 1 and 2 were applied. Before those fixes, the backend container exited at startup.

## Known Issues

Issues 1 and 2 are fixed in the repository. Issue 3 is open and needs a decision before changes are made.

1. **Fixed: missing `PASSWORD_RESET_SECRET`.** `app/auth/security.py` raises `RuntimeError` when the variable is unset. A placeholder was added to `.env.docker`. The placeholder is committed to git. Replace it with a real value from a non-committed source before real use.
2. **Fixed: missing system libraries for OpenCV.** `app/routes/upload.py` imports `cv2`, which failed with `libxcb.so.1: cannot open shared object file`. `backend/Dockerfile` now installs `libxcb1`, `libgl1`, and `libglib2.0-0`.
3. **Open: duplicate `DATABASE_URL`.** Defined in both `.env.docker` and the `environment` section of `compose.yaml`. Both values are identical. Proposed fix: keep one definition (for example, remove the `environment` block from `compose.yaml`).
4. **`load_dotenv(".env.example")` in `app/main.py` (no change).** `backend/.dockerignore` excludes `.env.*`, so the file is not in the image and this call does nothing inside Docker. Environment variables come from `.env.docker` through Compose. No change made.
5. **Crowd monitoring has no `/health` or `/docs` route.** The backend health check reports crowd as `ok` through its own check. The crowd UI is at `/demo` and the OpenAPI schema is at `/openapi.json`.
6. **Player service `/health` returns 404.** `/docs` returns 200.
7. **Database has no healthcheck in `compose.yaml`.** Dependent services can start before PostgreSQL accepts connections.
8. **Bind-mount folders missing from a fresh clone.** See [Folders Required by Bind Mounts](#folders-required-by-bind-mounts).
9. **Parallel first build stalled.** Observed once during package installation. Not reproduced when building services one at a time.
10. **Deprecated Dockerfile syntax.** `backend/Dockerfile` uses `FROM ... as base`. Should be `AS base`. Cosmetic.

## Known Working Commands

```bash
docker compose config --quiet
docker compose ps -a
docker compose exec -T db psql -U user -d orion_db -c "\dt"
docker compose down
docker compose up -d
```