from __future__ import annotations
import os, uuid
from datetime import datetime
from typing import Optional, Dict

from sqlalchemy import create_engine, func, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

# --- DB setup ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

# -------------------
# ORM models
# -------------------
class Upload(Base):
    __tablename__ = "uploads"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    media_type: Mapped[str] = mapped_column(String(32), nullable=False, default="video")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    original_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # 🔹 Cascade delete relationship to inferences
    inferences = relationship(
        "Inference",
        back_populates="upload",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class Inference(Base):
    __tablename__ = "inferences"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploads.id", ondelete="CASCADE"),   # 🔹 important
        nullable=False,
        index=True
    )
    task: Mapped[str] = mapped_column(String(16), nullable=False)  # "player" | "crowd"
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="ok")
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    upload = relationship("Upload", back_populates="inferences")


class PlayerAnalysis(Base):
    __tablename__ = "player_analysis"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upload_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("uploads.id"), nullable=False, index=True)
    player_id: Mapped[int] = mapped_column(Integer, nullable=False)
    json_path: Mapped[str] = mapped_column(String(512), nullable=False)
    heatmap_path: Mapped[str] = mapped_column(String(512), nullable=False)
    team_heatmap_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    
    # ✅ zone fields
    zone_back_50_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    zone_midfield_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    zone_forward_50_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)

    stats: Mapped[dict] = mapped_column(JSONB, nullable=True, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CrowdAnalysis(Base):
    __tablename__ = "crowd_analysis"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    upload_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("uploads.id"), nullable=False, index=True)
    frame_number: Mapped[int] = mapped_column(Integer, nullable=False)
    people_count: Mapped[int] = mapped_column(Integer, nullable=True)
    frame_image_path: Mapped[str] = mapped_column(String(512), nullable=False)
    heatmap_image_path: Mapped[str] = mapped_column(String(512), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


# -------------------
# Table creation
# -------------------
Base.metadata.create_all(bind=engine)

def _db():
    return SessionLocal()

# -------------------
# Upload helpers
# -------------------
def save_upload(path: str, media_type: str, size_bytes: int, user_id: int, original_filename: Optional[str] = None) -> dict:
    with _db() as db:
        row = Upload(
            path=path,
            media_type=media_type,
            size_bytes=size_bytes,
            user_id=user_id,
            original_filename=original_filename,  # ✅ save filename
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return {
            "id": str(row.id),
            "user_id": row.user_id,
            "path": row.path,
            "media_type": row.media_type,
            "size_bytes": row.size_bytes,
            "created_at": row.created_at.isoformat(),
            "original_filename": row.original_filename,  # ✅ include filename
        }

def get_upload(upload_id: str) -> Optional[dict]:
    from sqlalchemy.exc import NoResultFound
    with _db() as db:
        try:
            row = db.query(Upload).filter(Upload.id == uuid.UUID(upload_id)).one()
            return {
                "id": str(row.id),
                "user_id": row.user_id,
                "path": row.path,
                "media_type": row.media_type,
                "size_bytes": row.size_bytes,
                "created_at": row.created_at.isoformat(),
                "original_filename": row.original_filename,  # ✅ include filename
            }
        except NoResultFound:
            return None


# -------------------
# Player Analysis helpers
# -------------------
def get_player_analysis(upload_id: str, player_id: int) -> Optional[dict]:
    with _db() as db:
        row = db.query(PlayerAnalysis).filter(
            PlayerAnalysis.upload_id == uuid.UUID(upload_id),
            PlayerAnalysis.player_id == player_id
        ).first()
        if row:
            return {
                "id": row.id,
                "upload_id": str(row.upload_id),
                "player_id": row.player_id,
                "json_path": row.json_path,
                "heatmap_path": row.heatmap_path,
                "team_heatmap_path": row.team_heatmap_path,
                "stats": row.stats,
                "created_at": row.created_at.isoformat()
            }
        return None

def save_player_analysis(
    upload_id: str,
    player_id: int,
    json_path: str,
    heatmap_path: str,
    team_heatmap_path: Optional[str] = None,
    zone_back_50_path: Optional[str] = None,
    zone_midfield_path: Optional[str] = None,
    zone_forward_50_path: Optional[str] = None,
    stats: Optional[dict] = None
) -> dict:
    with _db() as db:
        row = db.query(PlayerAnalysis).filter(
            PlayerAnalysis.upload_id == uuid.UUID(upload_id),
            PlayerAnalysis.player_id == player_id
        ).first()

        if row:
            row.json_path = json_path or row.json_path
            row.heatmap_path = heatmap_path or row.heatmap_path
            row.team_heatmap_path = team_heatmap_path or row.team_heatmap_path
            row.zone_back_50_path = zone_back_50_path or row.zone_back_50_path
            row.zone_midfield_path = zone_midfield_path or row.zone_midfield_path
            row.zone_forward_50_path = zone_forward_50_path or row.zone_forward_50_path
            row.stats = stats or row.stats
        else:
            row = PlayerAnalysis(
                upload_id=uuid.UUID(upload_id),
                player_id=player_id,
                json_path=json_path,
                heatmap_path=heatmap_path,
                team_heatmap_path=team_heatmap_path,
                zone_back_50_path=zone_back_50_path,
                zone_midfield_path=zone_midfield_path,
                zone_forward_50_path=zone_forward_50_path,
                stats=stats or {}
            )
            db.add(row)

        db.commit()
        db.refresh(row)

        return {
            "id": row.id,
            "upload_id": str(row.upload_id),
            "player_id": row.player_id,
            "json_path": row.json_path,
            "heatmap_path": row.heatmap_path,
            "team_heatmap_path": row.team_heatmap_path,
            "zone_back_50_path": row.zone_back_50_path,
            "zone_midfield_path": row.zone_midfield_path,
            "zone_forward_50_path": row.zone_forward_50_path,
            "stats": row.stats,
            "created_at": row.created_at.isoformat()
        }

# -------------------
# Crowd Analysis helpers
# -------------------
def get_crowd_analysis(upload_id: str) -> list[dict]:
    """Fetch all crowd analysis entries for a video"""
    with _db() as db:
        rows = db.query(CrowdAnalysis).filter(
            CrowdAnalysis.upload_id == uuid.UUID(upload_id)
        ).order_by(CrowdAnalysis.frame_number).all()

        return [
            {
                "id": row.id,
                "upload_id": str(row.upload_id),
                "frame_number": row.frame_number,
                "people_count": row.people_count,
                "frame_image_path": row.frame_image_path,
                "heatmap_image_path": row.heatmap_image_path,
                "created_at": row.created_at.isoformat()
            }
            for row in rows
        ]


def save_crowd_analysis(
    upload_id: str,
    frame_number: int,
    people_count: int,
    frame_image_path: str,
    heatmap_image_path: str
) -> dict:
    """Save one crowd analysis record (per frame)"""
    with _db() as db:
        row = CrowdAnalysis(
            upload_id=uuid.UUID(upload_id),
            frame_number=frame_number,
            people_count=people_count,
            frame_image_path=frame_image_path,
            heatmap_image_path=heatmap_image_path,
        )
        db.add(row)
        db.commit()
        db.refresh(row)

        return {
            "id": row.id,
            "upload_id": str(row.upload_id),
            "frame_number": row.frame_number,
            "people_count": row.people_count,
            "frame_image_path": row.frame_image_path,
            "heatmap_image_path": row.heatmap_image_path,
            "created_at": row.created_at.isoformat()
        }



# -------------------
# Init check
# -------------------
def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT 1")


# -------------------
# Inference helpers
# -------------------
def save_inference(upload_id: str, user_id: int, task: str, status: str, payload: dict = None) -> dict:
    """Create a new inference if not exists, otherwise update the existing one"""
    with _db() as db:
        row = db.query(Inference).filter(
            Inference.upload_id == uuid.UUID(upload_id),
            Inference.task == task
        ).first()

        if row:
            # 🔹 Update existing record
            row.status = status
            row.payload = payload or row.payload
        else:
            # 🔹 Create new record
            row = Inference(
                upload_id=uuid.UUID(upload_id),
                user_id=user_id,
                task=task,
                status=status,
                payload=payload or {}
            )
            db.add(row)

        db.commit()
        db.refresh(row)

        return {
            "id": str(row.id),
            "upload_id": str(row.upload_id),
            "user_id": row.user_id,
            "task": row.task,
            "status": row.status,
            "payload": row.payload,
            "created_at": row.created_at.isoformat(),
        }


def get_inferences(upload_id: str) -> list[dict]:
    """Fetch all inferences for an upload (both player and crowd)"""
    with _db() as db:
        rows = db.query(Inference).filter(
            Inference.upload_id == uuid.UUID(upload_id)
        ).order_by(Inference.created_at).all()

        return [
            {
                "id": str(row.id),
                "upload_id": str(row.upload_id),
                "user_id": row.user_id,
                "task": row.task,
                "status": row.status,
                "payload": row.payload,
                "created_at": row.created_at.isoformat()
            }
            for row in rows
        ]

