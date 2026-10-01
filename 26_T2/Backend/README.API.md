# Backend API Guide

This document provides a simple overview of the Project Orion backend API.

## Backend API

The backend uses FastAPI and acts as the gateway between the frontend, player tracking service, crowd monitoring service, and database.

The backend runs on:

http://localhost:8000

Swagger documentation is available at:

http://localhost:8000/docs

## Main Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Checks that the backend is running |
| GET | `/health` | Checks backend and service health |
| GET | `/test` | Tests the backend API |
| POST | `/auth/register` | Creates a new user |
| POST | `/auth/login` | Logs a user in |
| POST | `/auth/refresh` | Refreshes the authentication token |
| POST | `/auth/logout` | Logs the current user out |
| GET | `/auth/me` | Returns the current user |
| POST | `/upload` | Uploads a video for processing |
| GET | `/status/{job_id}` | Checks processing status |
| GET | `/jobs` | Returns a list of jobs |
| GET | `/jobs/{job_id}` | Returns information about a specific job |
| POST | `/jobs/{job_id}/retry` | Retries a failed or partial job |
| POST | `/jobs/{job_id}/recover` | Recovers an interrupted or failed job |
| GET | `/jobs/{job_id}/heatmap` | Returns the crowd heatmap for a job |
| DELETE | `/jobs/{job_id}` | Deletes a job |
| POST | `/players` | Sends a video to the player tracking service |
| POST | `/crowd` | Sends a video to the crowd monitoring service |
| GET | `/analysis/{job_id}` | Returns analysis results for a specific job |
| GET | `/analytics/{job_id}` | Returns analytics results for a specific job |
| GET | `/crowd/{job_id}` | Returns crowd monitoring results for a specific job |
| GET | `/player-tracking/{job_id}` | Returns player tracking results for a specific job |

## Authentication

Protected endpoints require an access token.

The token is passed using:

Authorization: Bearer <access_token>

The backend also supports refresh tokens so that a new access token can be requested without requiring the user to log in again.

## Job Processing

When a video is uploaded, the backend creates a job and assigns it a unique job ID.

The job can contain information including:

- Current status
- Processing progress
- Retry count
- Start time
- Completion time
- Processing duration
- Failure reason
- Player tracking results
- Crowd monitoring results

This allows the backend to provide more detailed information about processing and failures.

The job ID is also used when retrieving the results of a particular video:

- `/analysis/{job_id}`
- `/analytics/{job_id}`
- `/crowd/{job_id}`
- `/player-tracking/{job_id}`

Using the job ID ensures that the results returned belong to the correct uploaded video rather than relying on the latest processed job.

## API Contract

More detailed request and response information can be found in:

API_CONTRACT.md