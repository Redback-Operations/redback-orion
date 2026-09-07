# Backend Database Guide

Project Orion uses PostgreSQL as the backend database.

## Database

The default database is:

orion_db

The database connection is configured using the DATABASE_URL environment variable.

Example:

DATABASE_URL=postgresql+asyncpg://postgres@localhost:5432/orion_db

## Main Tables

The backend currently uses tables including:

- users
- jobs
- refresh_tokens

## Users

The users table stores user account information.

Important fields include:

- user_id
- email
- username
- password
- role
- created_at

## Jobs

The jobs table stores information about video processing jobs.

Important fields include:

- job_id
- user_id
- status
- video_path
- player_result
- crowd_result
- error
- retry_count
- progress
- started_at
- completed_at
- failure_reason
- created_at
- updated_at

These fields allow the backend to track the processing lifecycle of each job and provide more useful information when processing fails.

## Refresh Tokens

The refresh_tokens table stores authentication refresh tokens.

Important fields include:

- refresh_token_id
- user_id
- token
- expires_at
- is_active
- created_at

## Database Models

The SQLAlchemy database models are located in:

app/models.py

## Creating the Database

If PostgreSQL is being run locally, connect using:

psql -U postgres

Then create the database:

CREATE DATABASE orion_db;

Exit PostgreSQL using:

\q

## Environment Configuration

Make sure the backend environment configuration contains the correct DATABASE_URL.

If the PostgreSQL username, password, host, port or database name changes, DATABASE_URL must also be updated.

## Job Tracking

The Job model includes additional fields for improved processing tracking.

retry_count records how many times a job has been retried.

progress records the current processing progress.

started_at records when processing started.

completed_at records when processing finished.

failure_reason records information about why processing failed.