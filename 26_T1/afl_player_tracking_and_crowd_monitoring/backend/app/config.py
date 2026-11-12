import os
from dotenv import load_dotenv

load_dotenv()


# =========================================================
# EXTERNAL SERVICES
# =========================================================

PLAYER_SERVICE_URL = os.getenv(
    "PLAYER_SERVICE_URL",
    "http://localhost:8080",
)

CROWD_SERVICE_URL = os.getenv(
    "CROWD_SERVICE_URL",
    "http://localhost:8002",
)


# =========================================================
# BACKEND
# =========================================================

BACKEND_PORT = int(
    os.getenv("BACKEND_PORT", "8000")
)

UPLOAD_DIR = os.getenv(
    "UPLOAD_DIR",
    "uploads",
)


# =========================================================
# MOCK SERVICES
# =========================================================

USE_MOCK_SERVICES = (
    os.getenv("USE_MOCK_SERVICES", "true").lower()
    == "true"
)

USE_MOCK_PLAYER = (
    os.getenv(
        "USE_MOCK_PLAYER",
        str(USE_MOCK_SERVICES),
    ).lower()
    == "true"
)

USE_MOCK_CROWD = (
    os.getenv(
        "USE_MOCK_CROWD",
        str(USE_MOCK_SERVICES),
    ).lower()
    == "true"
)


# =========================================================
# DATABASE
# =========================================================

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/orion_db",
)

# Railway/PostgreSQL providers normally supply:
#
# postgresql://...
#
# SQLAlchemy async requires:
#
# postgresql+asyncpg://...
#
# Convert automatically so the same application works
# locally and in production.

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+asyncpg://",
        1,
    )

elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1,
    )


# =========================================================
# JWT
# =========================================================

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
        "60",
    )
)


# =========================================================
# APPLICATION SETTINGS
# =========================================================

DEBUG = (
    os.getenv("DEBUG", "true").lower()
    == "true"
)

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
)


# =========================================================
# FRONTEND / CORS
# =========================================================

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:8081",
)


# =========================================================
# GOOGLE OAUTH
# =========================================================

GOOGLE_CLIENT_ID = os.getenv(
    "GOOGLE_CLIENT_ID",
    "",
)

GOOGLE_CLIENT_SECRET = os.getenv(
    "GOOGLE_CLIENT_SECRET",
    "",
)

GOOGLE_CALLBACK_URL = os.getenv(
    "GOOGLE_CALLBACK_URL",
    "http://localhost:8000/auth/google/callback",
)


# =========================================================
# MICROSOFT OAUTH / ENTRA ID
# =========================================================

MICROSOFT_CLIENT_ID = os.getenv(
    "MICROSOFT_CLIENT_ID",
    "",
)

# "common" allows:
# - Microsoft personal accounts
# - Work/school Microsoft accounts
#
# This matches the account type selected in Microsoft Entra.

MICROSOFT_TENANT_ID = os.getenv(
    "MICROSOFT_TENANT_ID",
    "common",
)

MICROSOFT_AUTHORITY = os.getenv(
    "MICROSOFT_AUTHORITY",
    f"https://login.microsoftonline.com/{MICROSOFT_TENANT_ID}",
)

MICROSOFT_OPENID_CONFIG_URL = os.getenv(
    "MICROSOFT_OPENID_CONFIG_URL",
    f"{MICROSOFT_AUTHORITY}/v2.0/.well-known/openid-configuration",
)

MICROSOFT_JWKS_URL = os.getenv(
    "MICROSOFT_JWKS_URL",
    "https://login.microsoftonline.com/common/discovery/v2.0/keys",
)