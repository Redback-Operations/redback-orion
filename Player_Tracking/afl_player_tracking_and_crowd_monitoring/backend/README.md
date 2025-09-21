📄 README.md (Backend Service)
# ⚡ Backend Service (FastAPI + PostgreSQL)

This backend service manages:
- Video uploads
- Player tracking inference (calls Player Tracking microservice)
- Crowd monitoring inference (calls external API provided by Son Tung Bui)
- Authentication (JWT)
- Analytics storage in PostgreSQL

---

## ⚙️ Requirements

- **Python 3.10** (recommended)
- **PostgreSQL 15** (via Docker or local installation)

---

## 📦 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<your-repo>.git
cd afl-redback-orion/Player_Tracking/afl_player_tracking_and_crowd_monitoring/backend

2. Create a virtual environment
py -3.10 -m venv venv
.\venv\Scripts\activate   # (Windows)
# or
source venv/bin/activate  # (Linux/Mac)

3. Upgrade pip
python -m pip install --upgrade pip

4. Install dependencies
pip install -r requirements.txt

🗄️ Run PostgreSQL in Docker

Run PostgreSQL locally in Docker:

docker run --name afl-postgres ^
  -e POSTGRES_USER=postgres ^
  -e POSTGRES_PASSWORD=postgres ^
  -e POSTGRES_DB=aflvision ^
  -p 5432:5432 ^
  -d postgres:15

⚙️ Environment Variables

Create a .env file inside the backend/ folder:

# Database connection
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/aflvision

# JWT secret key
JWT_SECRET=your-secret-key

🌐 Configure Crowd Monitoring API

Open:

backend/routes/crowd.py


Update this line with the API URL provided by Son Tung Bui:

CROWD_API_URL = "https://<provided-api-url>/analyze_frame/"

🚀 Run the Backend

Start the FastAPI server:

uvicorn main:app --reload --port 8000


Backend will run at:

http://127.0.0.1:8000


Swagger docs available at:

http://127.0.0.1:8000/docs

🧪 Example Workflow

Upload a video via backend → stored in uploaded_videos/.

Backend calls:

Player Tracking Service (http://127.0.0.1:8001)

Crowd Monitoring API (Son Tung Bui’s endpoint).

PostgreSQL stores analytics + user data.

Results available via API endpoints.

🛠️ Notes

Ensure PostgreSQL is running before starting backend.

Update CROWD_API_URL whenever Son Tung Bui provides a new endpoint (e.g., ngrok link).

Works best when combined with Player Tracking Service.