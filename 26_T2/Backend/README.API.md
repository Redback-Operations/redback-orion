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
| GET | `/health` | Checks backend and service health |
| POST | `/auth/register` | Creates a new user |
| POST | `/auth/login` | Logs a user in |
| GET | `/auth/me` | Returns the current user |
| POST | `/upload` | Uploads a video for processing |
| GET | `/status/{job_id}` | Checks processing status |
| GET | `/jobs` | Returns a list of jobs |
| GET | `/jobs/{job_id}` | Returns information about a specific job |
| POST | `/jobs/{job_id}/retry` | Retries a failed or partial job |
| DELETE | `/jobs/{job_id}` | Deletes a job |

## Authentication

Protected endpoints require an access token.

The token is passed using:

Authorization: Bearer <access_token>

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

## API Contract

More detailed request and response information can be found in:

API_CONTRACT.md