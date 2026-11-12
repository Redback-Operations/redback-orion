from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    create_async_engine,
)
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
    Session,
)

from app.config import DATABASE_URL, DEBUG


# =========================================================
# ASYNC DATABASE ENGINE
# =========================================================
#
# Used during FastAPI application startup to create/
# verify database tables.
#

engine = create_async_engine(
    DATABASE_URL,
    echo=DEBUG,
    pool_pre_ping=True,
)


# =========================================================
# SYNC DATABASE ENGINE
# =========================================================
#
# Existing routes/background tasks currently use
# synchronous SQLAlchemy sessions.
#

SYNC_DATABASE_URL = DATABASE_URL.replace(
    "postgresql+asyncpg://",
    "postgresql://",
    1,
)

sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=DEBUG,
    pool_pre_ping=True,
)


# =========================================================
# DATABASE SESSION
# =========================================================

SessionLocal = sessionmaker(
    bind=sync_engine,
    class_=Session,
    expire_on_commit=False,
)


# =========================================================
# BASE MODEL
# =========================================================

Base = declarative_base()


# =========================================================
# FASTAPI DATABASE DEPENDENCY
# =========================================================

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()