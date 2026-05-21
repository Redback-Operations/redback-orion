import asyncio
import copy
import httpx
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job
from app.schemas.jobs import JobDetail, JobListResponse, JobResults, JobErrors
from app.auth.dependencies import get_current_user
from app.config import CROWD_SERVICE_URL, PLAYER_SERVICE_URL

router = APIRouter()


def _crowd_with_urls(crowd: dict) -> dict:
    if not crowd:
        return crowd
    c = copy.deepcopy(crowd)
    base = f"{CROWD_SERVICE_URL}/artifacts/"

    for section in ("heatmap", "anomaly_visual", "time_series_chart"):
        path = c.get(section, {}) and c[section].get("image_path")
        if path and not path.startswith("http"):
            c[section]["image_path"] = base + path

    pcf = c.get("peak_crowd_frame")
    if pcf:
        for key in ("annotated_frame_path", "people_annotated_frame_path"):
            if pcf.get(key) and not pcf[key].startswith("http"):
                pcf[key] = base + pcf[key]

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
    if tackle and tackle.get("csv_url") and not tackle["csv_url"].startswith("http"):
        tackle["csv_url"] = base + tackle["csv_url"]

    tracking = p.get("tracking")
    if tracking and tracking.get("video_url") and not tracking["video_url"].startswith("http"):
        tracking["video_url"] = base + tracking["video_url"]

    return p


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
        response["results"] = {
            "player": _player_with_urls(job.player_result),
            "crowd": _crowd_with_urls(job.crowd_result),
        }
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
        results = JobResults(
            player=_player_with_urls(job.player_result),
            crowd=_crowd_with_urls(job.crowd_result),
        )
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
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.routes.upload import process_video

    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    check_job_access(job, current_user)
    if job.status != "partial":
        raise HTTPException(status_code=400, detail="Only partial jobs can be retried")
    if not job.video_path or not __import__("os").path.exists(job.video_path):
        raise HTTPException(status_code=409, detail="Original video no longer available for retry")

    job.status = "processing"
    job.player_result = None
    job.crowd_result = None
    job.error = None
    job.updated_at = datetime.utcnow()
    db.commit()

    background_tasks.add_task(process_video, str(job.job_id), job.video_path)

    return {"job_id": str(job.job_id), "status": "processing"}


@router.get("/jobs/{job_id}/heatmap")
async def get_heatmap(
    job_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.job_id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    check_job_access(job, current_user)

    crowd = job.crowd_result
    if not crowd or not crowd.get("heatmap") or not crowd["heatmap"].get("image_path"):
        raise HTTPException(status_code=404, detail="Heatmap not available for this job")

    image_path = crowd["heatmap"]["image_path"].replace("\\", "/")
    url = f"{CROWD_SERVICE_URL}/artifacts/{image_path}"

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(status_code=502, detail="Could not fetch heatmap from crowd service")

    return StreamingResponse(iter([r.content]), media_type="image/png")


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
