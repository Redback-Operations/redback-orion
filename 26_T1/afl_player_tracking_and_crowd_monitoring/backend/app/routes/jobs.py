import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job
from app.schemas.jobs import JobDetail, JobListResponse, JobResults, JobErrors
from app.auth.dependencies import get_current_user
from app.services.player_client import get_player_data
from app.services.crowd_client import get_crowd_data

router = APIRouter()


def check_job_access(job: Job, current_user: dict):
    if current_user["role"] != "admin" and str(job.user_id) != current_user["sub"]:
        raise HTTPException(status_code=403, detail="Access denied")


@router.get("/status/{job_id}")
def get_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    check_job_access(job, current_user)

    response = {"job_id": str(job.job_id), "status": job.status}
    if job.status != "processing":
        response["results"] = {"player": job.player_result, "crowd": job.crowd_result}
    if job.error:
        response["error"] = job.error
    return response


@router.get("/jobs", response_model=JobListResponse)
def list_jobs(
    page: int = 1,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Job)
    if current_user["role"] != "admin":
        query = query.filter(Job.user_id == current_user["sub"])

    total = query.count()
    jobs = query.order_by(Job.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    return {"total": total, "page": page, "limit": limit, "jobs": jobs}


@router.get("/jobs/{job_id}", response_model=JobDetail)
def get_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    check_job_access(job, current_user)

    results = None
    errors = None
    if job.status != "processing":
        results = JobResults(player=job.player_result, crowd=job.crowd_result)
        if job.status == "partial":
            errors = JobErrors(
                player="Service failed" if not job.player_result else None,
                crowd="Service failed" if not job.crowd_result else None
            )

    return {
        "job_id": str(job.job_id),
        "status": job.status,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "results": results,
        "errors": errors
    }


@router.post("/jobs/{job_id}/retry")
async def retry_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    check_job_access(job, current_user)
    if job.status != "partial":
        raise HTTPException(status_code=400, detail="Only partial jobs can be retried")

    retry_player = job.player_result is None
    retry_crowd = job.crowd_result is None

    tasks = []
    if retry_player:
        tasks.append(get_player_data(job.video_path))
    if retry_crowd:
        tasks.append(get_crowd_data(job.video_path))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    idx = 0
    if retry_player:
        r = results[idx]; idx += 1
        job.player_result = None if isinstance(r, Exception) else r
    if retry_crowd:
        r = results[idx]
        job.crowd_result = None if isinstance(r, Exception) else r

    if job.player_result and job.crowd_result:
        job.status = "done"
    elif not job.player_result and not job.crowd_result:
        job.status = "failed"
    else:
        job.status = "partial"

    job.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {"job_id": str(job.job_id), "status": job.status}


@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    check_job_access(job, current_user)
    db.delete(job)
    db.commit()
    return {"message": "job deleted"}
