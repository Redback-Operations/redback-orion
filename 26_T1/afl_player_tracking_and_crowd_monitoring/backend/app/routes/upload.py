import os
import uuid
import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models import Job
from app.schemas.jobs import UploadResponse
from app.auth.dependencies import get_current_user
from app.config import UPLOAD_DIR
from app.services.player_client import get_player_data
from app.services.crowd_client import get_crowd_data

from sqlalchemy import select

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov"}
ALLOWED_MIME_TYPES = {"video/mp4", "video/x-msvideo", "video/quicktime"}


async def process_video(job_id: str, file_path: str):
    db = SessionLocal()
    try:
        results = await asyncio.gather(
            get_player_data(file_path),
            get_crowd_data(file_path),
            return_exceptions=True
        )
        player_result, crowd_result = results

        player_error = str(player_result) if isinstance(player_result, Exception) else None
        crowd_error = str(crowd_result) if isinstance(crowd_result, Exception) else None

        player_data = None if isinstance(player_result, Exception) else player_result
        crowd_data = None if isinstance(crowd_result, Exception) else crowd_result

        if player_error and crowd_error:
            status = "failed"
            error = f"Player: {player_error} | Crowd: {crowd_error}"
        elif player_error or crowd_error:
            status = "partial"
            error = player_error or crowd_error
        else:
            status = "done"
            error = None

        result = await db.execute(select(Job).where(Job.job_id == job_id))
        job = result.scalar_one_or_none()
        if job:
            job.status = status
            job.player_result = player_data
            job.crowd_result = crowd_data
            job.error = error
            job.updated_at = datetime.now(timezone.utc)
            await db.commit()
    finally:
        await db.close()
        if os.path.exists(file_path):
            os.remove(file_path)


@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid video format. Accepted formats: .mp4, .avi, .mov"
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    job = Job(
        user_id=current_user["sub"],
        status="processing",
        video_path=file_path
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    background_tasks.add_task(process_video, str(job.job_id), file_path)

    return {
        "job_id": str(job.job_id),
        "status": job.status,
        "created_at": job.created_at
    }
