from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from app.config import DATABASE_URL

# Async engine — used only for lifespan table creation in main.py
engine = create_async_engine(DATABASE_URL, echo=True)

# Sync engine — used by all routes and background tasks
sync_engine = create_engine(DATABASE_URL.replace("+asyncpg", ""), echo=True)

SessionLocal = sessionmaker(bind=sync_engine, class_=Session, expire_on_commit=False)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
