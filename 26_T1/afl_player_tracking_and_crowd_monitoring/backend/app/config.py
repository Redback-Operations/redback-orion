import os

from dotenv import load_dotenv

load_dotenv()


PLAYER_SERVICE_URL = os.getenv(
    "PLAYER_SERVICE_URL",
    "http://localhost:8080",
).rstrip("/")


CROWD_SERVICE_URL = os.getenv(
    "CROWD_SERVICE_URL",
    "http://localhost:8002",
).rstrip("/")


BACKEND_PORT = int(
    os.getenv(
        "BACKEND_PORT",
        8000,
    )
)


UPLOAD_DIR = os.getenv(
    "UPLOAD_DIR",
    "uploads",
)


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/orion_db",
)


JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "your-secret-key-here",
)


JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
)


JWT_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_EXPIRE_MINUTES",
        60,
    )
)


DEBUG = (
    os.getenv(
        "DEBUG",
        "true",
    ).lower()
    == "true"
)


LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
)
