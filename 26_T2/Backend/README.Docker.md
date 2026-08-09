# Orion Backend Docker Setup

This document explains how to run the Orion project using Docker.

## Requirements

Before starting, make sure the following are installed:

- Docker Desktop
- Git

Docker Desktop must be running before using Docker commands.

## Services

The Docker environment can include:

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

## Start the Project

Make sure Docker Desktop is running.

From the directory containing `compose.yaml`, run:

```bash
docker compose up --build
```

Docker will build the required images and start the services.

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
docker compose up --build
```