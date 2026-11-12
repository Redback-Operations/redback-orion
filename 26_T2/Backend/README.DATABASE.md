# Database

This document provides an overview of the database used by the Project Orion backend.

## Overview

The backend uses PostgreSQL as its database and SQLAlchemy for database access.

The database stores user information, authentication data and video-processing jobs. Player Tracking and Crowd Monitoring results are also stored against their corresponding jobs.

## Database Connection

The database connection is configured using the `DATABASE_URL` environment variable.

Example:

`postgresql://username:password@localhost:5432/database_name`

When running through Docker, the PostgreSQL service name is used instead of `localhost`.

## Database Tables

The main database tables are:

- `users`
- `jobs`
- `refresh_tokens`

## Users Table

The `users` table stores information about registered users.

It is used by the authentication system and provides the relationship between a user and their processing jobs.

User information includes account details, authentication information and the user's role.

A single user can have multiple processing jobs.

## Jobs Table

The `jobs` table stores information about uploaded videos and their processing state.

Each job is identified using a unique `job_id`.

The main job information includes:

| Field | Description |
|---|---|
| `job_id` | Unique identifier for the processing job |
| `user_id` | User associated with the job |
| `status` | Current processing status |
| `video_path` | Location of the uploaded video |
| `player_result` | Result returned from Player Tracking |
| `crowd_result` | Result returned from Crowd Monitoring |
| `error` | Error information associated with processing |
| `retry_count` | Number of processing retries |
| `progress` | Current processing progress |
| `started_at` | Time processing started |
| `completed_at` | Time processing completed |
| `failure_reason` | Information explaining why processing failed |
| `created_at` | Time the job was created |
| `updated_at` | Time the job was last updated |

Player Tracking and Crowd Monitoring results are stored against the same job so that the backend can retrieve results for a specific uploaded video.

## Job Status and Progress

The backend tracks the state of each processing job.

The job status shows the current processing state, while `progress` provides additional information about how far the processing has progressed.

Processing timestamps are also stored so that the backend can track when processing started and completed.

If processing fails, the job can store error and failure information to help identify the cause.

## Job Results

Player Tracking results are stored in:

`player_result`

Crowd Monitoring results are stored in:

`crowd_result`

These results are linked to the unique `job_id`.

This allows the result APIs to retrieve information for a specific job:

`GET /analysis/{job_id}`

`GET /analytics/{job_id}`

`GET /player-tracking/{job_id}`

`GET /crowd/{job_id}`

## Retry and Recovery

The database stores information required by the backend's retry and recovery functionality.

The `retry_count` field tracks the number of retry attempts made for a job.

The backend can also use the stored video path, processing status, timestamps and failure information when determining whether a job can be retried or recovered.

## Refresh Tokens Table

The `refresh_tokens` table supports the authentication system.

Refresh tokens allow users to obtain a new access token without having to log in again each time their access token expires.

Refresh-token information is associated with the corresponding user.

## Database Relationships

The main relationships can be represented as:

User
 |
 +---- Jobs
 |
 +---- Refresh Tokens

A user can have multiple processing jobs and authentication-related refresh tokens.

Each processing job remains associated with the user who created it.

## Database Models

The SQLAlchemy database models are defined in:

`app/models.py`

Any future changes to the database structure should also be reflected in this documentation.