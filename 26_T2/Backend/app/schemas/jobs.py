from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_serializer
)


class UploadResponse(BaseModel):
    job_id: UUID
    status: str
    created_at: datetime

    @field_serializer("job_id")
    def serialize_uuid(
        self,
        value: UUID
    ) -> str:
        return str(value)


class JobSummary(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    job_id: UUID
    status: str

    retry_count: int = 0
    progress: int = 0

    created_at: datetime
    updated_at: datetime

    @field_serializer("job_id")
    def serialize_uuid(
        self,
        value: UUID
    ) -> str:
        return str(value)


class JobResults(BaseModel):
    player: Optional[Any] = None
    crowd: Optional[Any] = None


class JobErrors(BaseModel):
    player: Optional[str] = None
    crowd: Optional[str] = None


class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str

    health: str

    progress: int = 0
    retry_count: int = 0

    failed_components: List[str] = Field(
        default_factory=list
    )

    component_status: Dict[str, str] = Field(
        default_factory=dict
    )

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    processing_time: Optional[float] = None
    failure_reason: Optional[str] = None

    results: Optional[JobResults] = None
    error: Optional[str] = None

    @field_serializer("job_id")
    def serialize_uuid(
        self,
        value: UUID
    ) -> str:
        return str(value)


class JobRecoveryResponse(BaseModel):
    job_id: UUID
    status: str
    health: str
    retry_count: int

    @field_serializer("job_id")
    def serialize_uuid(
        self,
        value: UUID
    ) -> str:
        return str(value)


class JobDetail(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    job_id: UUID
    status: str

    retry_count: int = 0
    progress: int = 0

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    processing_time: Optional[float] = None
    failure_reason: Optional[str] = None

    health: Optional[str] = None

    failed_components: List[str] = Field(
        default_factory=list
    )

    component_status: Dict[str, str] = Field(
        default_factory=dict
    )

    created_at: datetime
    updated_at: datetime

    results: Optional[JobResults] = None
    errors: Optional[JobErrors] = None

    @field_serializer("job_id")
    def serialize_uuid(
        self,
        value: UUID
    ) -> str:
        return str(value)


class JobListResponse(BaseModel):
    total: int
    page: int
    limit: int
    jobs: List[JobSummary]