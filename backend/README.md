# Project Orion Backend

The Project Orion backend is built using FastAPI and acts as the main connection between the frontend, PostgreSQL database, Player Tracking service, and Crowd Monitoring service.

The backend handles user authentication, video uploads, processing jobs, communication with the ML services, result storage, and retrieval of analysis results.

## Main Features

- User authentication and role management
- Video upload and validation
- Player Tracking service integration
- Crowd Monitoring service integration
- Background job processing
- Job progress and status tracking
- Job-specific result retrieval
- Analysis and Analytics APIs
- Retry and recovery handling
- Result formatting for frontend use
- Backend testing and error handling

## Processing Flow

The main processing flow is:

**Frontend → Backend → Player Tracking / Crowd Monitoring → Backend → PostgreSQL → Frontend**

Each uploaded video creates a unique `job_id`. Player Tracking and Crowd Monitoring results are stored against this job, allowing the frontend to retrieve results for the correct video.

## Main Result APIs

GET /analysis/{job_id}
GET /analytics/{job_id}
GET /player-tracking/{job_id}
GET /crowd/{job_id}

## Running the Backend
Install the required dependencies:
pip install -r requirements.txt

## Start the FastAPI server:
uvicorn app.main:app --reload

The backend will normally be available at:
http://localhost:8000

Swagger API documentation:
http://localhost:8000/docs

## Docker
The backend can also be started using Docker Compose:
docker compose up --build

See README.Docker.md for more information about the Docker setup.
## Documentation
More detailed documentation is available in:
- README.API.md – API endpoints and usage
- README.ARCHITECTURE.md – backend architecture and processing flow
- README.DATABASE.md – database structure
- README.Docker.md – Docker setup
- API_CONTRACT.md – API request and response contracts
- RUN_TEST.md – testing instructions