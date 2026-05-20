import os
import uuid
import json
import csv
import asyncio
import tempfile
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.models import Job
from app.schemas.jobs import UploadResponse
from app.auth.dependencies import get_current_user
from app.config import UPLOAD_DIR
from app.services.player_client import (
    get_player_data,
    get_jersey_color_data,
    get_tackle_data,
    get_formation_data,
)
from app.services.crowd_client import get_crowd_data

router = APIRouter()

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov"}
ALLOWED_MIME_TYPES = {"video/mp4", "video/x-msvideo", "video/quicktime"}


def tracking_to_csv(tracking_results: list, csv_path: str):
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["frame_id", "timestamps_s", "player_id", "cx", "cy", "x1", "y1", "x2", "y2"]
        )
        writer.writeheader()
        for frame in tracking_results:
            for player in frame.get("players", []):
                writer.writerow({
                    "frame_id": frame["frame_number"],
                    "timestamps_s": frame["timestamp"],
                    "player_id": player["player_id"],
                    "cx": player["center"]["x"],
                    "cy": player["center"]["y"],
                    "x1": player["bbox"]["x1"],
                    "y1": player["bbox"]["y1"],
                    "x2": player["bbox"]["x2"],
                    "y2": player["bbox"]["y2"],
                })


async def process_video(job_id: str, file_path: str):
    db = SessionLocal()
    tmp_json = None
    tmp_csv = None

    try:
        # Step 1: tracking (required - all other steps depend on it)
        tracking_result = await get_player_data(file_path)

        # Step 2: save tracking JSON + build tackle CSV for downstream calls
        tmp_json = tempfile.NamedTemporaryFile(
            suffix="_tracking.json", delete=False, mode="w"
        )
        json.dump(tracking_result, tmp_json)
        tmp_json.close()
        tracking_json_path = tmp_json.name

        tmp_csv_file = tempfile.NamedTemporaryFile(
            suffix="_tracking.csv", delete=False
        )
        tmp_csv_file.close()
        tmp_csv = tmp_csv_file.name
        tracking_to_csv(tracking_result.get("tracking_results", []), tmp_csv)

        # Step 3: run jersey_color, formation, tackle + crowd in parallel
        jersey_task = get_jersey_color_data(file_path, tracking_json_path)
        formation_task = get_formation_data(file_path, tracking_json_path)
        tackle_task = get_tackle_data(tmp_csv)
        crowd_task = get_crowd_data(file_path)

        results = await asyncio.gather(
            jersey_task, formation_task, tackle_task, crowd_task,
            return_exceptions=True
        )
        jersey_result, formation_result, tackle_result, crowd_result = results

        player_result = {
            "tracking": tracking_result,
            "jersey_color": None if isinstance(jersey_result, Exception) else jersey_result,
            "formation": None if isinstance(formation_result, Exception) else formation_result,
            "tackle": None if isinstance(tackle_result, Exception) else tackle_result,
        }

        errors = []
        if isinstance(jersey_result, Exception):
            errors.append(f"jersey_color: {jersey_result}")
        if isinstance(formation_result, Exception):
            errors.append(f"formation: {formation_result}")
        if isinstance(tackle_result, Exception):
            errors.append(f"tackle: {tackle_result}")
        if isinstance(crowd_result, Exception):
            errors.append(f"crowd: {crowd_result}")

        crowd_data = None if isinstance(crowd_result, Exception) else crowd_result
        status = "done" if not errors else ("failed" if not player_result["tracking"] else "partial")

        job = db.query(Job).filter(Job.job_id == job_id).first()
        if job:
            job.status = status
            job.player_result = player_result
            job.crowd_result = crowd_data
            job.error = " | ".join(errors) if errors else None
            job.updated_at = datetime.utcnow()
            db.commit()

    except Exception as e:
        status = "failed"
        job = db.query(Job).filter(Job.job_id == job_id).first()
        if job:
            job.status = "failed"
            job.error = str(e)
            job.updated_at = datetime.utcnow()
            db.commit()
    finally:
        db.close()
        # Keep video file on partial so retry can reuse it; delete on done/failed
        if status != "partial" and os.path.exists(file_path):
            os.remove(file_path)
        if tmp_json and os.path.exists(tmp_json.name):
            os.remove(tmp_json.name)
        if tmp_csv and os.path.exists(tmp_csv):
            os.remove(tmp_csv)


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
    try:
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

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error while uploading video")
