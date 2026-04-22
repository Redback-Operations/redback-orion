import os
from dotenv import load_dotenv

load_dotenv()

PLAYER_SERVICE_URL = os.getenv("PLAYER_SERVICE_URL", "http://localhost:8001")
CROWD_SERVICE_URL = os.getenv("CROWD_SERVICE_URL", "http://localhost:8002")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8000))
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

USE_MOCK_SERVICES = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"

# Have just added async driver ('+asyncpg') to URL to match app - Lucas
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/orion_db")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

DEBUG = os.getenv("DEBUG", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


