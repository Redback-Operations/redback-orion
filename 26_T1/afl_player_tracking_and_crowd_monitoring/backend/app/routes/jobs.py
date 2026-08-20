import os
import uuid as uuid_module

import httpx

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
)

from fastapi.responses import (
    StreamingResponse,
)

from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
)

from app.config import (
    CROWD_SERVICE_URL,
)

from app.database import get_db

from app.models import Job

from app.schemas.jobs import (
    JobDetail,
    JobErrors,
    JobListResponse,
    JobResults,
)

from app.services.result_formatter import (
    crowd_with_urls,
    player_with_urls,
)

router = APIRouter()


def _parse_job_id(
    job_id: str,
):
    try:
        return uuid_module.UUID(job_id)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=("Invalid job_id format: " f"'{job_id}'"),
        ) from exc


def check_job_access(
    job: Job,
    current_user: dict,
):
    if current_user["role"] != "admin" and str(job.user_id) != current_user["sub"]:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )


def _user_jobs(
    db: Session,
    current_user: dict,
):
    query = db.query(Job)

    if current_user["role"] != "admin":
        query = query.filter(Job.user_id == current_user["sub"])

    return query


def _results(
    job: Job,
):
    return {
        "player": player_with_urls(job.player_result),
        "crowd": crowd_with_urls(job.crowd_result),
    }


@router.get("/status/{job_id}")
def get_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.job_id == _parse_job_id(job_id)).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    check_job_access(
        job,
        current_user,
    )

    response = {
        "job_id": str(job.job_id),
        "status": job.status,
        "created_at": (job.created_at),
        "updated_at": (job.updated_at),
    }

    if job.status != "processing":
        response["results"] = _results(job)

    if job.error:
        response["error"] = job.error

    return response


@router.get(
    "/jobs",
    response_model=JobListResponse,
)
def list_jobs(
    page: int = Query(
        default=1,
        ge=1,
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = _user_jobs(
        db,
        current_user,
    )

    total = query.count()

    jobs = (
        query.order_by(Job.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "jobs": jobs,
    }


@router.get("/jobs/latest")
def latest_job(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = (
        _user_jobs(
            db,
            current_user,
        )
        .filter(
            Job.status.in_(
                [
                    "done",
                    "partial",
                ]
            )
        )
        .order_by(Job.created_at.desc())
        .first()
    )

    if not job:
        raise HTTPException(
            status_code=404,
            detail=("No completed analysis " "is available"),
        )

    return {
        "job_id": str(job.job_id),
        "status": (job.status),
        "created_at": (job.created_at),
        "updated_at": (job.updated_at),
        "results": (_results(job)),
        "error": (job.error),
    }


@router.get(
    "/jobs/{job_id}",
    response_model=JobDetail,
)
def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.job_id == _parse_job_id(job_id)).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    check_job_access(
        job,
        current_user,
    )

    results = None
    errors = None

    if job.status != "processing":
        results = JobResults(
            player=player_with_urls(job.player_result),
            crowd=crowd_with_urls(job.crowd_result),
        )

        if job.status in (
            "partial",
            "failed",
        ):
            errors = JobErrors(
                player=("Player analysis failed" if not job.player_result else None),
                crowd=("Crowd analysis failed" if not job.crowd_result else None),
            )

    return {
        "job_id": str(job.job_id),
        "status": (job.status),
        "created_at": (job.created_at),
        "updated_at": (job.updated_at),
        "results": results,
        "errors": errors,
    }


@router.post("/jobs/{job_id}/retry")
def retry_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.routes.upload import (
        process_video,
    )

    job = db.query(Job).filter(Job.job_id == _parse_job_id(job_id)).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    check_job_access(
        job,
        current_user,
    )

    if job.status != "partial":
        raise HTTPException(
            status_code=400,
            detail=("Only partial jobs " "can be retried"),
        )

    if not job.video_path or not os.path.exists(job.video_path):
        raise HTTPException(
            status_code=409,
            detail=("Original video no longer " "available for retry"),
        )

    job.status = "processing"
    job.error = None

    db.commit()

    background_tasks.add_task(
        process_video,
        str(job.job_id),
        job.video_path,
    )

    return {
        "job_id": str(job.job_id),
        "status": "processing",
    }


@router.get("/jobs/{job_id}/heatmap")
async def get_heatmap(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.job_id == _parse_job_id(job_id)).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    check_job_access(
        job,
        current_user,
    )

    crowd = job.crowd_result or {}

    path = (crowd.get("heatmap") or {}).get("image_path")

    if not path:
        raise HTTPException(
            status_code=404,
            detail=("Heatmap not available " "for this job"),
        )

    if path.startswith("http"):
        url = path

    else:
        clean_path = path.replace(
            "\\",
            "/",
        ).lstrip("/")

        url = f"{CROWD_SERVICE_URL}" "/artifacts/" f"{clean_path}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:

            response = await client.get(url)

            response.raise_for_status()

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502,
            detail=("Could not fetch heatmap " "from crowd service"),
        ) from exc

    return StreamingResponse(
        iter([response.content]),
        media_type=(
            response.headers.get(
                "content-type",
                "image/png",
            )
        ),
    )


@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.job_id == _parse_job_id(job_id)).first()

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    check_job_access(
        job,
        current_user,
    )

    db.delete(job)

    db.commit()

    return {"message": "Job deleted"}
