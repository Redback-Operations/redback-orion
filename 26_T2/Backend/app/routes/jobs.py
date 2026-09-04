import copy
import uuid as _uuid
import httpx

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db, SessionLocal
from app.models import Job
from app.schemas.jobs import JobDetail, JobListResponse, JobResults, JobErrors
from app.auth.dependencies import get_current_user
from app.config import CROWD_SERVICE_URL, PLAYER_SERVICE_URL

from app.services.player_client import get_player_data
from app.services.crowd_client import get_crowd_data


router = APIRouter()

MAX_RETRIES = 3


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _crowd_with_urls(crowd: dict) -> dict:
    if not crowd:
        return crowd

    c = copy.deepcopy(crowd)
    base = f"{CROWD_SERVICE_URL}/artifacts/"

    for section in ("heatmap", "anomaly_visual", "time_series_chart"):
        path = c.get(section, {}) and c[section].get("image_path")

        if path and not path.startswith("http"):
            c[section]["image_path"] = base + path.replace("\\", "/")

    pcf = c.get("peak_crowd_frame")

    if pcf:
        for key in ("annotated_frame_path", "people_annotated_frame_path"):
            if pcf.get(key) and not pcf[key].startswith("http"):
                pcf[key] = base + pcf[key].replace("\\", "/")

    return c


def _player_with_urls(player: dict) -> dict:
    if not player:
        return player

    p = copy.deepcopy(player)
    base = PLAYER_SERVICE_URL

    for section in ("jersey_color", "formation"):
        sec = p.get(section)

        if not sec:
            continue

        for key in ("video_url", "csv_url"):
            if sec.get(key) and not sec[key].startswith("http"):
                sec[key] = base + sec[key]

    tackle = p.get("tackle")

    if (
        tackle
        and tackle.get("csv_url")
        and not tackle["csv_url"].startswith("http")
    ):
        tackle["csv_url"] = base + tackle["csv_url"]

    tracking = p.get("tracking")

    if (
        tracking
        and tracking.get("video_url")
        and not tracking["video_url"].startswith("http")
    ):
        tracking["video_url"] = base + tracking["video_url"]

    return p


def _parse_job_id(job_id: str) -> str:
    try:
        return str(_uuid.UUID(job_id))

    except ValueError:
        # Keep the value so the database lookup can return 404
        return job_id


def check_job_access(job: Job, current_user: dict):
    if (
        current_user["role"] != "admin"
        and str(job.user_id) != current_user["sub"]
    ):
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )


def _processing_time(job: Job):
    started_at = getattr(job, "started_at", None)
    completed_at = getattr(job, "completed_at", None)

    if started_at and completed_at:
        return (completed_at - started_at).total_seconds()

    return None


async def process_retry(job_id: str):
    db = SessionLocal()

    try:
        job = db.query(Job).filter(
            Job.job_id == job_id
        ).first()

        if not job:
            return

        try:
            if not job.player_result:
                job.player_result = await get_player_data(
                    job.video_path
                )

            if not job.crowd_result:
                job.crowd_result = await get_crowd_data(
                    job.video_path
                )

            if job.player_result and job.crowd_result:
                job.status = "done"
                job.progress = 100
                job.failure_reason = None
                job.error = None

            else:
                job.status = "partial"
                job.progress = 100
                job.failure_reason = (
                    "One or more services failed during retry"
                )

        except Exception as e:
            job.status = "partial"
            job.progress = 100
            job.failure_reason = str(e)
            job.error = str(e)

        job.completed_at = _now()
        job.updated_at = _now()

        db.commit()

    finally:
        db.close()


@router.get("/status/{job_id}")
def get_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    check_job_access(job, current_user)

    response = {
        "job_id": str(job.job_id),
        "status": job.status,
        "progress": getattr(job, "progress", 0),
        "retry_count": getattr(job, "retry_count", 0),
        "started_at": getattr(job, "started_at", None),
        "completed_at": getattr(job, "completed_at", None),
        "processing_time": _processing_time(job),
        "failure_reason": getattr(job, "failure_reason", None)
    }

    if job.status != "processing":
        response["results"] = {
            "player": _player_with_urls(job.player_result),
            "crowd": _crowd_with_urls(job.crowd_result)
        }

    if getattr(job, "error", None):
        response["error"] = job.error

    return response


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    page: int = 1,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
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
            detail="Limit must be between 1 and 100"
        )

    query = db.query(Job)

    if current_user["role"] != "admin":
        query = query.filter(
            Job.user_id == current_user["sub"]
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


@router.get("/jobs/{job_id}", response_model=JobDetail)
def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    check_job_access(job, current_user)

    results = None
    errors = None

    if job.status != "processing":
        results = JobResults(
            player=_player_with_urls(job.player_result),
            crowd=_crowd_with_urls(job.crowd_result)
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
        "created_at": job.created_at,
        "updated_at": job.updated_at,

        "retry_count": getattr(job, "retry_count", 0),
        "progress": getattr(job, "progress", 0),
        "started_at": getattr(job, "started_at", None),
        "completed_at": getattr(job, "completed_at", None),
        "processing_time": _processing_time(job),
        "failure_reason": getattr(job, "failure_reason", None),

        "results": results,
        "errors": errors
    }


@router.post("/jobs/{job_id}/retry")
async def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    check_job_access(job, current_user)

    if job.status != "partial":
        raise HTTPException(
            status_code=400,
            detail="Only partial jobs can be retried"
        )

    if not job.video_path:
        raise HTTPException(
            status_code=409,
            detail="Original video no longer available for retry"
        )

    retry_count = getattr(job, "retry_count", 0)

    if retry_count >= MAX_RETRIES:
        raise HTTPException(
            status_code=429,
            detail="Maximum retry limit reached"
        )

    job.retry_count = retry_count + 1
    job.status = "processing"
    job.progress = 0
    job.started_at = _now()
    job.completed_at = None
    job.failure_reason = None
    job.error = None
    job.updated_at = _now()

    db.commit()

    background_tasks.add_task(
        process_retry,
        str(job.job_id)
    )

    return {
        "job_id": str(job.job_id),
        "status": "processing",
        "retry_count": job.retry_count
    }


@router.get("/jobs/{job_id}/heatmap")
async def get_heatmap(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    check_job_access(job, current_user)

    crowd = job.crowd_result

    if (
        not crowd
        or not crowd.get("heatmap")
        or not crowd["heatmap"].get("image_path")
    ):
        raise HTTPException(
            status_code=404,
            detail="Heatmap not available for this job"
        )

    image_path = crowd["heatmap"]["image_path"].replace(
        "\\",
        "/"
    )

    url = f"{CROWD_SERVICE_URL}/artifacts/{image_path}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response.raise_for_status()

    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Crowd service timed out while fetching heatmap"
        )

    except httpx.ConnectError:
        raise HTTPException(
            status_code=502,
            detail="Crowd service is unavailable"
        )

    except httpx.HTTPStatusError:
        raise HTTPException(
            status_code=502,
            detail="Could not fetch heatmap from crowd service"
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Crowd service request failed"
        )

    return StreamingResponse(
        iter([response.content]),
        media_type="image/png"
    )


@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
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

    check_job_access(job, current_user)

    db.delete(job)
    db.commit()

    return {
        "message": "job deleted"
    }