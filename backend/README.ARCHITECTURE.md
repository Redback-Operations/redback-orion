# Backend Architecture

This document provides a simple overview of the Project Orion backend architecture.

## Overview

The backend acts as the main gateway between the frontend and the processing services.

The main components are:

Frontend
    |
    v
Backend Gateway
    |
    +---- Player Tracking Service
    |
    +---- Crowd Monitoring Service
    |
    v
PostgreSQL Database

The backend manages communication between these components and ensures that processing results are linked to the correct uploaded video using a unique `job_id`.

## Backend Gateway

The backend gateway is built using FastAPI.

It is responsible for:

- Receiving requests from the frontend
- User authentication and role management
- Video uploads and validation
- Creating processing jobs
- Tracking job status and progress
- Communicating with processing services
- Storing processing results
- Formatting results for frontend use
- Returning job-specific results to the frontend
- Handling processing failures
- Supporting job retry and recovery
- Providing Analysis and Analytics APIs

## Player Tracking Service

The Player Tracking service processes uploaded footage and returns player-related analysis to the backend.

The backend communicates with this service through the player service client.

Player Tracking results are stored against the corresponding processing job and can be retrieved using the job ID:

`GET /player-tracking/{job_id}`

The backend also formats Player Tracking results into a consistent structure before returning them to the frontend.

## Crowd Monitoring Service

The Crowd Monitoring service processes footage for crowd-related analysis.

The backend communicates with this service through the crowd service client.

Crowd Monitoring results are stored against the corresponding processing job and can be retrieved using:

`GET /crowd/{job_id}`

The backend also supports retrieving crowd heatmap information when it is available for a job.

## Database

PostgreSQL is used to store backend information.

This includes:

- Users
- Authentication information
- Processing jobs
- Job status
- Job progress
- Player Tracking results
- Crowd Monitoring results
- Retry information
- Processing timestamps
- Failure information

Each processing job has a unique `job_id`, which allows results and processing information to remain associated with the correct uploaded video.

## Job Processing

When a video is uploaded:

1. The backend receives and validates the video.
2. A new job with a unique `job_id` is created.
3. The video is sent to the Player Tracking and Crowd Monitoring services.
4. The backend tracks the progress of the job.
5. Results returned by the processing services are stored against the job.
6. Errors and failure information are recorded if processing does not complete successfully.
7. The frontend can request the current job status and results using the `job_id`.

The backend also supports additional job information such as retry counts, progress, processing timestamps and failure reasons.

Jobs that fail or become interrupted can also use the retry and recovery functionality provided by the backend.

## Result Retrieval

Processing results are retrieved using the `job_id` associated with the uploaded video.

The main result endpoints are:

`GET /analysis/{job_id}`

`GET /analytics/{job_id}`

`GET /player-tracking/{job_id}`

`GET /crowd/{job_id}`

The Analysis API provides the processing results for a specific job, while the Analytics API provides summarised information from the stored Player Tracking and Crowd Monitoring results.

Using job-specific endpoints prevents results from different uploaded videos from being mixed together.

## Main Backend Files

`app/main.py`

Starts and configures the FastAPI backend and registers the backend routes.

`app/models.py`

Defines the database models for users, processing jobs and authentication information.

`app/schemas/jobs.py`

Defines the API schemas used for job information and responses.

`app/routes/`

Contains the backend API routes, including authentication, uploads, jobs, Analysis, Analytics, Player Tracking and Crowd Monitoring.

`app/services/`

Contains the clients used to communicate with the Player Tracking and Crowd Monitoring services, along with supporting backend service logic.

`app/services/result_formatter.py`

Formats processing results into structures that can be consistently returned through the backend APIs.

`app/database.py`

Handles the PostgreSQL database connection.

`app/config.py`

Contains backend configuration and settings used for the database and processing services.