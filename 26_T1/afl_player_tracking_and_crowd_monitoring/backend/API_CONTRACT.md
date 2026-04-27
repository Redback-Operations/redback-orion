# Project Orion — API Contract
**Version:** 1.2.0  
**Date:** 2026-04-27  
**Backend Lead:** Tomin Jose  
**Base URL:** `http://localhost:8000`  
**Interactive Docs:** `http://localhost:8000/docs`

---

## Overview

This document defines every HTTP endpoint the frontend must integrate with. All endpoints return JSON. All timestamps are ISO 8601 UTC strings.

---

## Authentication

All protected endpoints require a JWT token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

The system uses **two tokens**:

| Token | Lifetime | Purpose |
|-------|----------|---------|
| `access_token` | 60 minutes | Attached to every API request |
| `refresh_token` | 7 days | Used only to silently get a new access token |

Both tokens are returned on login and register. When an `access_token` expires the frontend receives a `401` — at that point call `POST /auth/refresh` with the `refresh_token` to get a new pair silently. Do **not** redirect to login unless the refresh token is also expired or revoked.

---

## Error Response Format

All errors follow this consistent shape:

```json
{
  "detail": "Human-readable error message"
}
```

| HTTP Status | Meaning |
|-------------|---------|
| `400` | Bad request — validation error or invalid input |
| `401` | Unauthorized — missing or expired token |
| `403` | Forbidden — valid token but insufficient role |
| `404` | Resource not found |
| `500` | Internal server error |

---

## Endpoints

---

### 1. Health Check

#### `GET /health`
No authentication required.

**Response `200`:**
```json
{
  "gateway": "ok",
  "player_service": "ok | pending | error",
  "crowd_service": "ok | pending | error"
}
```

**Use:** Check on app startup to verify services are reachable.

---

#### `GET /`
No authentication required.

**Response `200`:**
```json
{
  "status": "success",
  "message": "Backend is running!"
}
```

---

### 2. Authentication

---

#### `POST /auth/register`
Create a new user account. Returns a token immediately — no separate login needed after registration.

**Request body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepassword"
}
```

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `username` | string | Yes | Must be unique |
| `email` | string (email) | Yes | Must be unique, valid email format |
| `password` | string | Yes | Stored as bcrypt hash |

**Response `200`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "username": "johndoe",
    "email": "john@example.com",
    "role": "user",
    "created_at": "2026-04-06T10:00:00Z"
  }
}
```

**Error responses:**
```json
// 400 — email already registered
{ "detail": "Email already registered" }

// 400 — username already taken
{ "detail": "Username already taken" }
```

---

#### `POST /auth/login`
Authenticate an existing user and receive both tokens.

**Request body:**
```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "username": "johndoe",
    "email": "john@example.com",
    "role": "user",
    "created_at": "2026-04-06T10:00:00Z"
  }
}
```

**Error responses:**
```json
// 401 — wrong credentials
{ "detail": "Invalid email or password" }
```

---

#### `POST /auth/refresh`
Exchange a valid refresh token for a new access token + refresh token pair. The old refresh token is revoked immediately after use.

**Request body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `200`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": { ... }
}
```

**Error responses:**
```json
// 401 — token invalid, expired, or already revoked
{ "detail": "Invalid or expired refresh token" }
{ "detail": "Refresh token has been revoked" }
{ "detail": "Refresh token has expired" }
```

> Always replace both stored tokens with the new pair returned. The old refresh token cannot be reused.

---

#### `POST /auth/logout`
Revoke the refresh token. After this the user must log in again when their access token expires.

**Request body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response `200`:**
```json
{
  "message": "Logged out successfully"
}
```

> After calling logout, clear both tokens from storage on the frontend.

---

#### `GET /auth/me`
**Protected.** Get the currently logged-in user's profile.

**Response `200`:**
```json
{
  "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "johndoe",
  "email": "john@example.com",
  "role": "user",
  "created_at": "2026-04-06T10:00:00Z"
}
```

> `role` is either `"user"` or `"admin"`. Use this to conditionally show admin-only UI.

---

### 3. Video Upload

---

#### `POST /upload`
**Protected.** Upload a video file for analysis. Returns a `job_id` immediately — processing happens in the background.

**Request:** `multipart/form-data`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `file` | file | Yes | Accepted: `.mp4`, `.avi`, `.mov` |

**Example (JavaScript fetch):**
```js
const formData = new FormData();
formData.append('file', videoFile);

const response = await fetch('http://localhost:8000/upload', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});
```

**Response `200`:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "processing",
  "created_at": "2026-04-06T10:00:00Z"
}
```

**Error responses:**
```json
// 400 — unsupported file format
{ "detail": "Invalid video format. Accepted formats: .mp4, .avi, .mov" }

// 401 — not logged in
{ "detail": "Not authenticated" }
```

> After receiving `job_id`, immediately begin polling `/status/{job_id}`.

---

### 4. Job Status & Results

---

#### `GET /status/{job_id}`
**Protected.** Poll this endpoint to check processing progress.

**Path parameter:** `job_id` — UUID returned from `/upload`

**Response while processing `200`:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "processing"
}
```

**Response when complete `200`:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "done",
  "results": {
    "player": { ... },
    "crowd": { ... }
  }
}
```

**Response when partial (one service failed) `200`:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "partial",
  "results": {
    "player": { ... },
    "crowd": null
  },
  "error": "Crowd service timed out"
}
```

**Response when failed `200`:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "failed",
  "error": "Player: timeout | Crowd: timeout"
}
```

**Job status values:**

| Status | Meaning | Frontend action |
|--------|---------|-----------------|
| `processing` | Both services still running | Keep polling |
| `done` | Both services succeeded | Display full results |
| `partial` | One service failed, one succeeded | Display partial results + show retry button |
| `failed` | Both services failed | Show error message |

**Recommended polling interval:** every **4 seconds** until status is not `processing`.

**Error responses:**
```json
// 404
{ "detail": "Job not found" }

// 403 — trying to access another user's job
{ "detail": "Access denied" }
```

---

#### `GET /jobs`
**Protected.** List all jobs for the current user (paginated). Admins see all jobs.

**Query parameters:**

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `page` | integer | `1` | Page number |
| `limit` | integer | `10` | Results per page |

**Example:** `GET /jobs?page=2&limit=5`

**Response `200`:**
```json
{
  "total": 42,
  "page": 2,
  "limit": 5,
  "jobs": [
    {
      "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "status": "done",
      "created_at": "2026-04-06T10:00:00Z",
      "updated_at": "2026-04-06T10:01:30Z"
    },
    ...
  ]
}
```

---

#### `GET /jobs/{job_id}`
**Protected.** Get full detail of a single job including results.

**Response `200`:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "done",
  "created_at": "2026-04-06T10:00:00Z",
  "updated_at": "2026-04-06T10:01:30Z",
  "results": {
    "player": {
      "players": [
        {
          "player_id": 1,
          "team": "Team A",
          "position": { "x": 120, "y": 340 },
          "speed": 6.4,
          "distance_covered": 3.2,
          "sprints": 4
        }
      ],
      "heatmap": null
    },
    "crowd": {
      "video_id": "8d41b321-2870-45a0-9bf7-4faa05293511",
      "summary": {
        "total_frames_processed": 65,
        "peak_person_count": 11,
        "crowd_state": "increasing_density",
        "highest_density_zone": "B2",
        "highest_risk_zone": "B2"
      },
      "peak_crowd_frame": {
        "frame_id": 49,
        "timestamp": 8.0,
        "person_count": 11,
        "annotated_frame_path": "crowd_detection_output/people_detection_results/frame_0049.jpg"
      },
      "anomaly_visual": {
        "event_type": "walking_or_running_activity",
        "image_path": "crowd_behaviour_analytics/output/.../motion_frame_0009.jpg"
      },
      "heatmap": {
        "image_path": "output/heatmap_8d41b321-....png"
      },
      "time_series_chart": {
        "image_path": "analytics_output/charts/8d41b321-..._crowd_activity_chart.png"
      },
      "density_extremes": {
        "highest_density_zone": {
          "zone_id": "B2",
          "person_count": 227,
          "density": 1.0,
          "risk_level": "critical",
          "flagged": true
        },
        "lowest_density_zone": {
          "zone_id": "A1",
          "person_count": 0,
          "density": 0.0,
          "risk_level": "very_low",
          "flagged": false
        }
      }
    }
  },
  "errors": {
    "player": null,
    "crowd": null
  }
}
```

**Crowd state values:**

| Value | Meaning |
|-------|---------|
| `increasing_density` | Crowd is growing in density |
| `stable` | Crowd density is steady |
| `decreasing_density` | Crowd is thinning out |

**Risk level values:** `very_low`, `low`, `medium`, `high`, `critical`

> Do **not** use `crowd.heatmap.image_path` directly — it is a server-side file path. Use `GET /jobs/{job_id}/heatmap` to fetch the heatmap image.

---

#### `GET /jobs/{job_id}/heatmap`
**Protected.** Fetch the heatmap PNG image for a completed job.

**Response `200`:** PNG image (`Content-Type: image/png`)

**Usage in frontend:**
```js
const url = `http://localhost:8000/jobs/${jobId}/heatmap`;
// Use directly as <img src={url} /> with the Authorization header via fetch
```

**Error responses:**
```json
// 404 — heatmap not ready yet or job not found
{ "detail": "Heatmap not available for this job" }

// 502 — crowd service unreachable
{ "detail": "Could not fetch heatmap from crowd service" }
```

---

### 5. Job Actions

---

#### `POST /jobs/{job_id}/retry`
**Protected.** Re-run only the failed service for a `partial` job. Only works when `status === "partial"`.

**Request body:** none

**Response `200`:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "done"
}
```

**Error responses:**
```json
// 400 — job is not partial
{ "detail": "Only partial jobs can be retried" }

// 404
{ "detail": "Job not found" }
```

> After retry, resume polling `/status/{job_id}` until status changes from `processing`.

---

#### `DELETE /jobs/{job_id}`
**Protected.** Permanently delete a job record.

**Response `200`:**
```json
{
  "message": "job deleted"
}
```

**Error responses:**
```json
// 404
{ "detail": "Job not found" }

// 403
{ "detail": "Access denied" }
```

---

## CORS

The backend is configured to accept requests from `http://localhost:3000`. No proxy configuration is needed.

Allowed:
- **Origins:** `http://localhost:3000`
- **Methods:** All (`GET`, `POST`, `PUT`, `DELETE`, etc.)
- **Headers:** All
- **Credentials:** Yes

---

## Frontend Integration Checklist

```
Auth
[ ] Store access_token AND refresh_token on login/register
[ ] Attach Authorization: Bearer <access_token> to every request
[ ] On 401 response → call POST /auth/refresh with refresh_token
[ ] If refresh succeeds → retry the original request with new access_token
[ ] If refresh fails (401) → clear tokens and redirect to /login
[ ] On logout → call POST /auth/logout, then clear both tokens from storage
[ ] Read role from /auth/me to show/hide admin UI

Upload
[ ] Send multipart/form-data — do NOT set Content-Type header manually
[ ] Show upload progress indicator
[ ] Save job_id from response and start polling immediately

Polling
[ ] Poll /status/{job_id} every 4 seconds
[ ] Stop polling when status !== "processing"
[ ] Handle all 4 status values: processing / done / partial / failed
[ ] Show retry button only when status === "partial"

Jobs History
[ ] Implement pagination using page + limit query params
[ ] Calculate total pages: Math.ceil(total / limit)

Error Handling
[ ] Handle 400, 401, 403, 404, 500 globally
[ ] Show user-friendly messages from the detail field
[ ] Never expose raw token values in UI or logs
```

---

## Notes

- The `results.crowd` schema is **confirmed** — see `GET /jobs/{job_id}` above for the full structure returned by the real crowd model.
- The `results.player` schema is **TBC** — pending player service integration. Currently returns mock data with `players[]` array and `heatmap`.
- Do **not** use image paths from `crowd_result` directly. Always use `GET /jobs/{job_id}/heatmap` to fetch images via the gateway.
- Swagger UI at `http://localhost:8000/docs` is live and can be used to test all endpoints directly.
- All `job_id` and `user_id` values are **UUIDs** (string format: `"3fa85f64-5717-4562-b3fc-2c963f66afa6"`).
- Refresh tokens are **single use** — each call to `/auth/refresh` revokes the old token and issues a new pair.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.2.0 | 2026-04-27 | Added confirmed crowd response schema. Added `GET /jobs/{job_id}/heatmap` proxy endpoint. Added split mock flags (`USE_MOCK_PLAYER` / `USE_MOCK_CROWD`). Crowd service integrated and tested end-to-end. |
| 1.1.0 | 2026-04-13 | Added refresh token flow — `POST /auth/refresh`, `POST /auth/logout`. Updated `/auth/register` and `/auth/login` responses to include `refresh_token`. Updated auth checklist. |
| 1.0.0 | 2026-04-06 | Initial contract — health, auth, upload, jobs, CORS, checklist. |
