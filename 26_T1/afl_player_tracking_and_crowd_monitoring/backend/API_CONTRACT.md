# Project Orion — API Contract
**Version:** 1.1.0  
**Date:** 2026-04-13  
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
    "player": { ... },
    "crowd": { ... }
  },
  "errors": {
    "player": null,
    "crowd": null
  }
}
```

> `results.player` and `results.crowd` schemas will be updated once the player and crowd teams finalise their service contracts. For now, treat them as arbitrary JSON objects.

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

- The `results.player` and `results.crowd` schemas are **TBC** — pending contract from the player and crowd service teams. The backend stores them as raw JSON (`JSONB`) and passes them through unchanged.
- Swagger UI at `http://localhost:8000/docs` is live and can be used to test all endpoints directly.
- All `job_id` and `user_id` values are **UUIDs** (string format: `"3fa85f64-5717-4562-b3fc-2c963f66afa6"`).
- Refresh tokens are **single use** — each call to `/auth/refresh` revokes the old token and issues a new pair.

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-04-13 | Added refresh token flow — `POST /auth/refresh`, `POST /auth/logout`. Updated `/auth/register` and `/auth/login` responses to include `refresh_token`. Updated auth checklist. |
| 1.0.0 | 2026-04-06 | Initial contract — health, auth, upload, jobs, CORS, checklist. |
