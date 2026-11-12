# Services Folder

This folder contains the shared service layer for the Crowd Monitoring module.

## Recommended Structure

```text
services/
|- README.md
|- main.py
|- routes.py
|- crowd_detection_service.py
|- crowd_analytics_service.py
`- crowd_intelligence_service.py
```

## Folder Purpose

This folder does not contain the full implementation of each task.

Instead, it provides the service flow:

- receive API request
- route the request
- call functions from task folders
- return structured JSON output

## File Purpose

### `main.py`

- creates the FastAPI application
- loads the routes

### `routes.py`

- contains the API endpoints
- calls the correct service file for each endpoint

### `crowd_detection_service.py`

- calls task implementations from:
  - `video_processing/main.py`
  - `crowd_detection/main.py`

### `crowd_analytics_service.py`

- calls task implementations from:
  - `density_zoning/main.py`
  - `heatmap/main.py`

### `crowd_intelligence_service.py`

- calls task implementations from:
  - `crowd_behaviour_analytics/main.py`
  - `crowd_allocation_risk_zone/main.py`

## Service Flow

```text
Request
-> routes.py
-> related service file
-> task folder implementation
-> result returned as JSON
```

## Important Rule

- task folders contain the implementation
- service files call task functions
- routes define endpoints
- `main.py` starts the API app

Keep this folder thin and simple. Do not duplicate business logic here if it already exists in a task folder.
