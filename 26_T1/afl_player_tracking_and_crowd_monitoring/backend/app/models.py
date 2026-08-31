import uuid

from datetime import (
    datetime,
    timezone,
)

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
    UUID,
)

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

    created_at = Column(
        DateTime,
        default=_now,
    )

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
        autoincrement=True,
    )

    name = Column(
        String,
        nullable=False,
        index=True,
    )

    team = Column(
        String,
        nullable=False,
        index=True,
    )

    position = Column(
        String,
        nullable=False,
        index=True,
    )

    photo = Column(
        Text,
        nullable=True,
    )

    kicks = Column(
        Integer,
        default=0,
        nullable=False,
    )

    handballs = Column(
        Integer,
        default=0,
        nullable=False,
    )

    marks = Column(
        Integer,
        default=0,
        nullable=False,
    )

    tackles = Column(
        Integer,
        default=0,
        nullable=False,
    )

    goals = Column(
        Integer,
        default=0,
        nullable=False,
    )

    efficiency = Column(
        Float,
        default=0,
        nullable=False,
    )

    age = Column(
        Integer,
        default=0,
        nullable=False,
    )

    height = Column(
        String,
        nullable=True,
    )

    weight = Column(
        String,
        nullable=True,
    )

    jerseyNumber = Column(
        Integer,
        default=0,
        nullable=False,
    )

    inside50s = Column(
        Integer,
        default=0,
        nullable=False,
    )

    disposals = Column(
        Integer,
        default=0,
        nullable=False,
    )

    teamLogo = Column(
        Text,
        nullable=True,
    )

    notes = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime,
        default=_now,
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=_now,
        onupdate=_now,
        nullable=False,
    )
