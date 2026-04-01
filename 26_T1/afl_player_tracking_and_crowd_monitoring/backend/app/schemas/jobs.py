from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime


class UploadResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime


class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    status: str
    created_at: datetime
    updated_at: datetime


class JobResults(BaseModel):
    player: Optional[Any] = None
    crowd: Optional[Any] = None


class JobErrors(BaseModel):
    player: Optional[str] = None
    crowd: Optional[str] = None


class JobDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    results: Optional[JobResults] = None
    errors: Optional[JobErrors] = None


class JobListResponse(BaseModel):
    total: int
    page: int
    limit: int
    jobs: List[JobSummary]
