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

## Backend Gateway

The backend gateway is built using FastAPI.

It is responsible for:

- Receiving requests from the frontend
- User authentication
- Video uploads
- Creating processing jobs
- Tracking job progress
- Communicating with processing services
- Returning results to the frontend
- Handling processing failures

## Player Tracking Service

The player tracking service processes uploaded footage and returns player-related analysis to the backend.

The backend communicates with this service through the player service client.

## Crowd Monitoring Service

The crowd monitoring service processes footage for crowd-related analysis.

The backend communicates with this service through the crowd service client.

## Database

PostgreSQL is used to store backend information.

This includes:

- Users
- Authentication information
- Processing jobs
- Job status
- Processing results
- Retry information
- Failure information

## Job Processing

When a video is uploaded:

1. The backend receives the video.
2. A new job is created.
3. The video is sent for processing.
4. The backend tracks the progress of the job.
5. Results or errors are recorded.
6. The frontend can request the current job status and results.

The backend also supports additional job information such as retry counts, progress, processing timestamps and failure reasons.

## Main Backend Files

`app/main.py`

Starts and configures the FastAPI backend.

`app/models.py`

Defines the database models.

`app/schemas/jobs.py`

Defines the API schemas used for job information.

`app/routes/`

Contains the backend API routes.

`app/services/`

Contains the clients used to communicate with the player and crowd services.

`app/database.py`

Handles the PostgreSQL database connection.