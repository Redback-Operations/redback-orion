import copy
import os
import uuid as _uuid

import httpx

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException
)

from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user

from app.config import (
    CROWD_SERVICE_URL,
    PLAYER_SERVICE_URL
)

from app.database import get_db
from app.models import Job

from app.schemas.jobs import (
    JobDetail,
    JobErrors,
    JobListResponse,
    JobRecoveryResponse,
    JobResults,
    JobStatusResponse
)

from app.services.job_manager import (
    can_retry_job,
    get_component_status,
    get_failed_components,
    get_job_health,
    get_processing_time,
    is_job_stuck,
    prepare_retry,
    process_retry
)


router = APIRouter()


def _crowd_with_urls(crowd: dict) -> dict:
    if not crowd:
        return crowd

    copied = copy.deepcopy(crowd)

    base = f"{CROWD_SERVICE_URL}/artifacts/"

    for section in (
        "heatmap",
        "anomaly_visual",
        "time_series_chart"
    ):
        path = (
            copied.get(section, {})
            and copied[section].get(
                "image_path"
            )
        )

        if path and not path.startswith("http"):
            copied[section]["image_path"] = (
                base + path.replace("\\", "/")
            )

    peak_frame = copied.get(
        "peak_crowd_frame"
    )

    if peak_frame:
        for key in (
            "annotated_frame_path",
            "people_annotated_frame_path"
        ):
            path = peak_frame.get(key)

            if path and not path.startswith("http"):
                peak_frame[key] = (
                    base + path.replace("\\", "/")
                )

    return copied


def _player_with_urls(player: dict) -> dict:
    if not player:
        return player

    copied = copy.deepcopy(player)

    base = PLAYER_SERVICE_URL

    for section in (
        "jersey_color",
        "formation"
    ):
        section_data = copied.get(section)

        if not section_data:
            continue

        for key in (
            "video_url",
            "csv_url"
        ):
            path = section_data.get(key)

            if path and not path.startswith("http"):
                section_data[key] = (
                    base + path
                )

    tackle = copied.get("tackle")

    if (
        tackle
        and tackle.get("csv_url")
        and not tackle["csv_url"].startswith("http")
    ):
        tackle["csv_url"] = (
            base + tackle["csv_url"]
        )

    tracking = copied.get("tracking")

    if (
        tracking
        and tracking.get("video_url")
        and not tracking["video_url"].startswith("http")
    ):
        tracking["video_url"] = (
            base + tracking["video_url"]
        )

    return copied


def _parse_job_id(job_id: str) -> str:
    try:
        return str(
            _uuid.UUID(job_id)
        )

    except ValueError:
        return job_id


def check_job_access(
    job: Job,
    current_user: dict
):
    if (
        current_user["role"] != "admin"
        and str(job.user_id)
        != current_user["sub"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )


def _get_job(
    job_id: str,
    db: Session
):
    job_id = _parse_job_id(job_id)

    job = db.query(Job).filter(
        Job.job_id == job_id
    ).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


def _add_retry_background_task(
    background_tasks: BackgroundTasks,
    job: Job,
    db: Session
):
    testing = (
        os.getenv("TESTING", "false").lower()
        == "true"
    )

    if testing:
        background_tasks.add_task(
            process_retry,
            str(job.job_id),
            db
        )

    else:
        background_tasks.add_task(
            process_retry,
            str(job.job_id)
        )


@router.get(
    "/status/{job_id}",
    response_model=JobStatusResponse
)
def get_status(
    job_id: str,
    current_user: dict = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db)
):
    job = _get_job(
        job_id,
        db
    )

    check_job_access(
        job,
        current_user
    )

    response = {
        "job_id": str(job.job_id),

        "status": job.status,

        "health": get_job_health(job),

        "progress": getattr(
            job,
            "progress",
            0
        ),

        "retry_count": getattr(
            job,
            "retry_count",
            0
        ),

        "failed_components":
            get_failed_components(job),

        "component_status":
            get_component_status(job),

        "started_at": getattr(
            job,
            "started_at",
            None
        ),

        "completed_at": getattr(
            job,
            "completed_at",
            None
        ),

        "processing_time":
            get_processing_time(job),

        "failure_reason": getattr(
            job,
            "failure_reason",
            None
        )
    }

    if job.status != "processing":
        response["results"] = {
            "player": _player_with_urls(
                job.player_result
            ),

            "crowd": _crowd_with_urls(
                job.crowd_result
            )
        }

    if getattr(job, "error", None):
        response["error"] = job.error

    return response


@router.get(
    "/jobs",
    response_model=JobListResponse
)
def list_jobs(
    page: int = 1,
    limit: int = 10,

    current_user: dict = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):
    if page < 1:
        raise HTTPException(
            status_code=400,
            detail="Page must be 1 or greater"
        )

    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail=(
                "Limit must be between "
                "1 and 100"
            )
        )

    query = db.query(Job)

    if current_user["role"] != "admin":
        query = query.filter(
            Job.user_id
            == current_user["sub"]
        )

    total = query.count()

    jobs = (
        query
        .order_by(Job.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "jobs": jobs
    }


@router.get(
    "/jobs/{job_id}",
    response_model=JobDetail
)
def get_job(
    job_id: str,

    current_user: dict = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):
    job = _get_job(
        job_id,
        db
    )

    check_job_access(
        job,
        current_user
    )

    results = None
    errors = None

    if job.status != "processing":
        results = JobResults(
            player=_player_with_urls(
                job.player_result
            ),

            crowd=_crowd_with_urls(
                job.crowd_result
            )
        )

        if job.status == "partial":
            errors = JobErrors(
                player=(
                    "Service failed"
                    if not job.player_result
                    else None
                ),

                crowd=(
                    "Service failed"
                    if not job.crowd_result
                    else None
                )
            )

    return {
        "job_id": str(job.job_id),
        "status": job.status,

        "health":
            get_job_health(job),

        "failed_components":
            get_failed_components(job),

        "component_status":
            get_component_status(job),

        "retry_count": getattr(
            job,
            "retry_count",
            0
        ),

        "progress": getattr(
            job,
            "progress",
            0
        ),

        "started_at": getattr(
            job,
            "started_at",
            None
        ),

        "completed_at": getattr(
            job,
            "completed_at",
            None
        ),

        "processing_time":
            get_processing_time(job),

        "failure_reason": getattr(
            job,
            "failure_reason",
            None
        ),

        "created_at":
            job.created_at,

        "updated_at":
            job.updated_at,

        "results":
            results,

        "errors":
            errors
    }


@router.post(
    "/jobs/{job_id}/retry"
)
async def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks,

    current_user: dict = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):
    job = _get_job(
        job_id,
        db
    )

    check_job_access(
        job,
        current_user
    )

    if job.status != "partial":
        raise HTTPException(
            status_code=400,
            detail=(
                "Only partial jobs "
                "can be retried"
            )
        )

    if not getattr(
        job,
        "video_path",
        None
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Original video no longer "
                "available for retry"
            )
        )

    if not prepare_retry(job):
        raise HTTPException(
            status_code=429,
            detail=(
                "Maximum retry "
                "limit reached"
            )
        )

    db.commit()

    _add_retry_background_task(
        background_tasks,
        job,
        db
    )

    return {
        "job_id":
            str(job.job_id),

        "status":
            "processing",

        "retry_count":
            job.retry_count
    }


@router.post(
    "/jobs/{job_id}/recover",
    response_model=JobRecoveryResponse
)
async def recover_job(
    job_id: str,
    background_tasks: BackgroundTasks,

    current_user: dict = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):
    job = _get_job(
        job_id,
        db
    )

    check_job_access(
        job,
        current_user
    )

    recoverable = (
        job.status == "partial"
        or is_job_stuck(job)
    )

    if not recoverable:
        raise HTTPException(
            status_code=400,
            detail=(
                "Job does not require "
                "recovery"
            )
        )

    if not getattr(
        job,
        "video_path",
        None
    ):
        raise HTTPException(
            status_code=409,
            detail=(
                "Original video no longer "
                "available for recovery"
            )
        )

    if not can_retry_job(job):
        raise HTTPException(
            status_code=429,
            detail=(
                "Job cannot be recovered "
                "because the retry limit "
                "has been reached"
            )
        )

    prepare_retry(job)

    db.commit()

    _add_retry_background_task(
        background_tasks,
        job,
        db
    )

    return {
        "job_id":
            str(job.job_id),

        "status":
            "processing",

        "health":
            "processing",

        "retry_count":
            job.retry_count
    }


@router.get(
    "/jobs/{job_id}/heatmap"
)
async def get_heatmap(
    job_id: str,

    current_user: dict = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):
    job = _get_job(
        job_id,
        db
    )

    check_job_access(
        job,
        current_user
    )

    crowd = job.crowd_result

    if (
        not crowd
        or not crowd.get("heatmap")
        or not crowd[
            "heatmap"
        ].get("image_path")
    ):
        raise HTTPException(
            status_code=404,
            detail=(
                "Heatmap not available "
                "for this job"
            )
        )

    image_path = (
        crowd[
            "heatmap"
        ][
            "image_path"
        ].replace(
            "\\",
            "/"
        )
    )

    url = (
        f"{CROWD_SERVICE_URL}"
        f"/artifacts/"
        f"{image_path}"
    )

    try:
        async with httpx.AsyncClient(
            timeout=10.0
        ) as client:
            response = await client.get(
                url
            )

            response.raise_for_status()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail=(
                "Crowd service timed out "
                "while fetching heatmap"
            )
        )

    except httpx.ConnectError:
        raise HTTPException(
            status_code=502,
            detail=(
                "Crowd service "
                "is unavailable"
            )
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail=(
                "Could not fetch heatmap "
                "from crowd service"
            )
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail=(
                "Crowd service "
                "request failed"
            )
        )

    return StreamingResponse(
        iter([
            response.content
        ]),
        media_type="image/png"
    )


@router.delete(
    "/jobs/{job_id}"
)
def delete_job(
    job_id: str,

    current_user: dict = Depends(
        get_current_user
    ),

    db: Session = Depends(get_db)
):
    job = _get_job(
        job_id,
        db
    )

    check_job_access(
        job,
        current_user
    )

    db.delete(job)
    db.commit()

    return {
        "message":
            "job deleted"
    }