from pydantic import BaseModel, ConfigDict, field_serializer
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID


class UploadResponse(BaseModel):
    job_id: UUID
    status: str
    created_at: datetime

    @field_serializer("job_id")
    def serialize_job_id(self, v: UUID) -> str:
        return str(v)


class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    @field_serializer("job_id")
    def serialize_job_id(self, v: UUID) -> str:
        return str(v)


class JobResults(BaseModel):
    player: Optional[Any] = None
    crowd: Optional[Any] = None


class JobErrors(BaseModel):
    player: Optional[str] = None
    crowd: Optional[str] = None


class JobDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    results: Optional[JobResults] = None
    errors: Optional[JobErrors] = None

    @field_serializer("job_id")
    def serialize_job_id(self, v: UUID) -> str:
        return str(v)


class JobListResponse(BaseModel):
    total: int
    page: int
    limit: int
    jobs: List[JobSummary]
