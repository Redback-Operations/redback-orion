import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.database import Base


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email = Column(
        String,
        unique=True,
        nullable=False,
    )

    username = Column(
        String,
        unique=True,
        nullable=False,
    )

    password = Column(
        String,
        nullable=False,
    )

    role = Column(
        String,
        default="user",
        nullable=False,
    )

    # Task 2:
    # Links a user account to an existing player.
    # Normal users/admins/coaches can leave this as NULL.
    player_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=_now,
    )

    player = relationship("Player")

    jobs = relationship(
        "Job",
        back_populates="user",
    )

    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
    )


class Job(Base):
    __tablename__ = "jobs"

    job_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False,
    )

    status = Column(
        String,
        default="processing",
        nullable=False,
    )

    video_path = Column(
        String,
        nullable=True,
    )

    player_result = Column(
        JSONB,
        nullable=True,
    )

    crowd_result = Column(
        JSONB,
        nullable=True,
    )

    error = Column(
        String,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=_now,
    )

    updated_at = Column(
        DateTime,
        default=_now,
        onupdate=_now,
    )

    user = relationship(
        "User",
        back_populates="jobs",
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    refresh_token_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id"),
        nullable=False,
    )

    token = Column(
        String,
        nullable=False,
        unique=True,
        index=True,
    )

    expires_at = Column(
        DateTime,
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    created_at = Column(
        DateTime,
        default=_now,
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="refresh_tokens",
    )


class Player(Base):
    __tablename__ = "players"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String,
        nullable=False,
    )

    team = Column(
        String,
        nullable=False,
    )

    position = Column(
        String,
        nullable=False,
    )

    photo = Column(
        Text,
        nullable=True,
    )

    kicks = Column(
        Integer,
        default=0,
    )

    handballs = Column(
        Integer,
        default=0,
    )

    marks = Column(
        Integer,
        default=0,
    )

    tackles = Column(
        Integer,
        default=0,
    )

    goals = Column(
        Integer,
        default=0,
    )

    efficiency = Column(
        Integer,
        default=75,
    )

    age = Column(
        Integer,
        default=0,
    )

    height = Column(
        String,
        nullable=True,
    )

    weight = Column(
        String,
        nullable=True,
    )

    jersey_number = Column(
        Integer,
        default=0,
    )

    inside50s = Column(
        Integer,
        default=0,
    )

    disposals = Column(
        Integer,
        default=0,
    )

    team_logo = Column(
        String,
        nullable=True,
    )

    notes = Column(
        Text,
        nullable=True,
    )