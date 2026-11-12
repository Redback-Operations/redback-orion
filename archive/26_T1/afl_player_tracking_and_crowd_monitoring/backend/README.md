# Backend — Project Orion

FastAPI gateway that connects the frontend to the AFL player tracking and crowd monitoring microservices.

---

## Architecture

```
Frontend (localhost:3000)
        │
        ▼
Backend Gateway  (localhost:8000)   ← this folder
        ├──▶ Player Service  (localhost:8080)
        └──▶ Crowd Service   (localhost:8002)
        │
        ▼
PostgreSQL (localhost:5432)
```

---

## Prerequisites

Install these before starting:

| Tool | Version | Download |
|------|---------|----------|
| Python | 3.11+ | https://python.org |
| PostgreSQL | 14+ | https://postgresql.org |

Verify your installs:

```powershell
python --version
psql --version
```

---

## First-Time Setup

Follow these steps in order. You only need to do this once.

---

### Step 1 — Create the PostgreSQL database

Open a terminal and run:

```powershell
psql -U postgres
```

Then inside the psql prompt:

```sql
CREATE DATABASE orion_db;
\q
```

> If your PostgreSQL user is not `postgres`, replace it with your username in the command above and in the `.env` file below.

---

### Step 2 — Install backend dependencies

```powershell
cd backend
pip install -r requirements.txt
```

---

### Step 3 — Create the `.env` file

Create a file called `.env` inside the `backend/` folder with this content:

```env
# Service URLs
PLAYER_SERVICE_URL=http://localhost:8080
CROWD_SERVICE_URL=http://localhost:8002
BACKEND_PORT=8000
UPLOAD_DIR=uploads

# Set both to false to use the real services
USE_MOCK_PLAYER=false
USE_MOCK_CROWD=false

# PostgreSQL — replace 'postgres' with your username if different
DATABASE_URL=postgresql+asyncpg://postgres@localhost:5432/orion_db

# Auth
JWT_SECRET_KEY=your-secret-key-change-this
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Optional
DEBUG=true
LOG_LEVEL=INFO
```

> The database tables are created automatically on first start — no migration step needed.

---

### Step 4 — Install player service dependencies

```powershell
cd player_service
pip install -r requirements.txt
```

---

### Step 5 — Install crowd service dependencies

```powershell
cd Crowd_Monitoring/2026_T1
pip install -r requirements.txt
```

---

## Running All Services

From the **project root** (the folder containing `start_all.ps1`), run:

```powershell
.\start_all.ps1
```

This starts all three services and prints a health check after 10 seconds:

```
Starting Player Service (port 8080)...
Starting Crowd Service (port 8002)...
Starting Backend Gateway (port 8000)...
Waiting for services to start...

Checking services:
  Player Service (8080): OK
  Crowd Service  (8002): OK
  Backend Gateway(8000): OK

All services started. Swagger UI: http://localhost:8000/docs
```

---

## Running Services Manually

If you need to start them individually (e.g. for debugging), open a separate terminal for each:

**Backend Gateway**
```powershell
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Player Service**
```powershell
cd player_service
python -m uvicorn main:app --host 0.0.0.0 --port 8080
```

**Crowd Service**
```powershell
cd Crowd_Monitoring/2026_T1
python -m uvicorn shared.services.main:app --host 0.0.0.0 --port 8002
```

> Always use `python -m uvicorn` (not `uvicorn` directly) on Windows to avoid import errors.

---

## Verify Everything Is Running

Once started, open these URLs in your browser:

| Service | URL |
|---------|-----|
| Backend Swagger | http://localhost:8000/docs |
| Backend health check | http://localhost:8000/health |
| Player Service Swagger | http://localhost:8080/docs |
| Crowd Service Swagger | http://localhost:8002/ |
| Crowd Demo UI | http://localhost:8002/demo |

---

## API Endpoints

All protected endpoints require the header:
```
Authorization: Bearer <access_token>
```

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | No | Check all services are reachable |
| POST | `/auth/register` | No | Create account, returns tokens |
| POST | `/auth/login` | No | Login, returns tokens |
| POST | `/auth/refresh` | No | Exchange refresh token for new token pair |
| POST | `/auth/logout` | No | Revoke refresh token |
| GET | `/auth/me` | JWT | Current user profile |
| POST | `/upload` | JWT | Upload video and start processing |
| GET | `/status/{job_id}` | JWT | Poll job status |
| GET | `/jobs` | JWT | List jobs (paginated) |
| GET | `/jobs/{job_id}` | JWT | Full job detail with results |
| POST | `/jobs/{job_id}/retry` | JWT | Retry a partial job |
| DELETE | `/jobs/{job_id}` | JWT | Delete a job |
| GET | `/jobs/{job_id}/heatmap` | JWT | Proxy heatmap image from crowd service |

See [API_CONTRACT.md](API_CONTRACT.md) for full request/response schemas and a Quick Start code example.

---

## How Processing Works

1. `POST /upload` saves the video and immediately returns a `job_id`
2. In the background: **tracking** runs first (required), then **jersey color + formation + tackle + crowd** run in parallel
3. Results are stored in PostgreSQL
4. `GET /status/{job_id}` returns the current status — poll every 4 seconds until it is not `processing`

**Job status values:**

| Status | Meaning |
|--------|---------|
| `processing` | Still running |
| `done` | All results available |
| `partial` | One service failed — retry available |
| `failed` | Both services failed |

---

## Mock vs Real Services

If you want to test the gateway without running the player or crowd services, set the mock flags in `.env`:

```env
USE_MOCK_PLAYER=true   # returns hardcoded player data
USE_MOCK_CROWD=true    # returns hardcoded crowd data
```

Restart the backend after changing `.env`.

---

## Troubleshooting

**`Address already in use` on startup**

A previous Python process is still holding the port. Kill all Python processes:

```powershell
Get-Process python | Stop-Process -Force
```

Then re-run `start_all.ps1`.

---

**`ModuleNotFoundError` when starting a service**

Make sure you installed dependencies for that specific service (Steps 2, 4, 5) and that you are running with `python -m uvicorn`, not `uvicorn` directly.

---

**Database connection error**

- Confirm PostgreSQL is running: `pg_ctl status` or check Services in Windows
- Confirm the database exists: `psql -U postgres -c "\l"`
- Confirm `DATABASE_URL` in `.env` matches your PostgreSQL username

---

**`401 Unauthorized` in Swagger**

Click the **Authorize** button (lock icon) at the top right of the Swagger page, enter your token in the `Value` field as:
```
Bearer <your_access_token>
```

---

**Crowd service images not loading**

Make sure the crowd service is running on port 8002 — it serves image files via its `/artifacts/` static file mount.
