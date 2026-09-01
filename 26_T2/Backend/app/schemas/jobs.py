from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    job_id: UUID
    status: str

    model_config = ConfigDict(from_attributes=True)


class JobSummary(BaseModel):
    job_id: UUID
    status: str
    retry_count: int = 0
    progress: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobDetail(BaseModel):
    job_id: UUID
    user_id: UUID
    status: str

    retry_count: int = 0
    progress: int = 0

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    processing_duration: Optional[float] = None

    failure_reason: Optional[str] = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)