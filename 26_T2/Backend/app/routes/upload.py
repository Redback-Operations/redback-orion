import asyncio
import csv
import json
import os
import tempfile
import uuid
import logging
import traceback

from datetime import (
    datetime,
    timezone,
)

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_current_user,
)

from app.config import (
    UPLOAD_DIR,
)

from app.database import (
    SessionLocal,
    get_db,
)

from app.models import Job

from app.schemas.jobs import (
    UploadResponse,
)

from app.services.crowd_client import (
    get_crowd_data,
)

from app.services.player_client import (
    get_formation_data,
    get_jersey_color_data,
    get_player_data,
    get_tackle_data,
)

router = APIRouter()
logger = logging.getLogger(__name__)


ALLOWED_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
}


ALLOWED_MIME_TYPES = {
    "video/mp4",
    "video/x-msvideo",
    "video/quicktime",
}


def tracking_to_csv(
    tracking_results: list,
    csv_path: str,
):
    with open(
        csv_path,
        "w",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "frame_id",
                "timestamps_s",
                "player_id",
                "cx",
                "cy",
                "x1",
                "y1",
                "x2",
                "y2",
            ],
        )

        writer.writeheader()

        for frame in tracking_results:

            for player in frame.get(
                "players",
                [],
            ):
                center = player.get("center") or {}

                bbox = player.get("bbox") or {}

                writer.writerow(
                    {
                        "frame_id": (frame.get("frame_number")),
                        "timestamps_s": (frame.get("timestamp")),
                        "player_id": (player.get("player_id")),
                        "cx": (center.get("x")),
                        "cy": (center.get("y")),
                        "x1": (bbox.get("x1")),
                        "y1": (bbox.get("y1")),
                        "x2": (bbox.get("x2")),
                        "y2": (bbox.get("y2")),
                    }
                )


async def process_video(
    job_id: str,
    file_path: str,
):
    db = SessionLocal()

    tmp_json_path = None
    tmp_csv_path = None

    status = "processing"

    try:
        print(f"[{job_id}] Starting player tracking")
        print(f"[{job_id}] Video path: {file_path}")
        print(f"[{job_id}] Video exists: {os.path.exists(file_path)}")
        print(
            f"[{job_id}] Video size: "
            f"{os.path.getsize(file_path) if os.path.exists(file_path) else 0} bytes"
        )
        # PLAYER TRACKING
        tracking_result = await get_player_data(file_path)
        print(f"[{job_id}] Player tracking completed")
        if not isinstance(
            tracking_result,
            dict,
        ):
            raise RuntimeError(
                "Player tracking service " "returned an invalid response"
            )

        # TEMP TRACKING JSON
        with tempfile.NamedTemporaryFile(
            suffix="_tracking.json",
            delete=False,
            mode="w",
            encoding="utf-8",
        ) as tmp_json:

            json.dump(
                tracking_result,
                tmp_json,
            )

            tmp_json_path = tmp_json.name

        # TEMP TRACKING CSV
        with tempfile.NamedTemporaryFile(
            suffix="_tracking.csv",
            delete=False,
        ) as tmp_csv:

            tmp_csv_path = tmp_csv.name

        tracking_to_csv(
            tracking_result.get(
                "tracking_results",
                [],
            ),
            tmp_csv_path,
        )

        # OTHER SERVICES
        (
            jersey_result,
            formation_result,
            tackle_result,
            crowd_result,
        ) = await asyncio.gather(
            get_jersey_color_data(
                file_path,
                tmp_json_path,
            ),
            get_formation_data(
                file_path,
                tmp_json_path,
            ),
            get_tackle_data(tmp_csv_path),
            get_crowd_data(file_path),
            return_exceptions=True,
        )

        # PLAYER RESULT
        player_result = {
            "tracking": (tracking_result),
            "jersey_color": (
                None
                if isinstance(
                    jersey_result,
                    Exception,
                )
                else jersey_result
            ),
            "formation": (
                None
                if isinstance(
                    formation_result,
                    Exception,
                )
                else formation_result
            ),
            "tackle": (
                None
                if isinstance(
                    tackle_result,
                    Exception,
                )
                else tackle_result
            ),
        }

        errors = []

        if isinstance(
            jersey_result,
            Exception,
        ):
            errors.append("jersey_color: " f"{jersey_result}")

        if isinstance(
            formation_result,
            Exception,
        ):
            errors.append("formation: " f"{formation_result}")

        if isinstance(
            tackle_result,
            Exception,
        ):
            errors.append("tackle: " f"{tackle_result}")

        if isinstance(
            crowd_result,
            Exception,
        ):
            errors.append("crowd: " f"{crowd_result}")

        crowd_data = (
            None
            if isinstance(
                crowd_result,
                Exception,
            )
            else crowd_result
        )

        status = "done" if not errors else "partial"

        # STORE REAL ML OUTPUT
        job = db.query(Job).filter(Job.job_id == uuid.UUID(job_id)).first()

        if job:
            job.status = status

            job.player_result = player_result

            job.crowd_result = crowd_data

            job.error = " | ".join(errors) if errors else None

            job.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
            
            job.progress = 100
            
            job.completed_at = (datetime.now(timezone.utc).replace(tzinfo=None))
            
            db.commit()

    except Exception as exc:
        status = "failed"

        error_message = f"{type(exc).__name__}: {exc!r}"

        logger.exception(
            "Video processing failed for job %s",
            job_id,
        )

        print("\n========== VIDEO PROCESSING ERROR ==========")
        print(f"Job ID: {job_id}")
        print(f"Exception type: {type(exc).__name__}")
        print(f"Exception repr: {repr(exc)}")
        traceback.print_exc()
        print("============================================\n")

        job = (
            db.query(Job)
            .filter(Job.job_id == uuid.UUID(job_id))
            .first()
        )

        if job:
            job.status = "failed"
            job.error = error_message
            job.failure_reason = error_message
            job.completed_at = (
                datetime.now(timezone.utc)
                .replace(tzinfo=None)
            )
            job.updated_at = (
                datetime.now(timezone.utc)
                .replace(tzinfo=None)
            )

            db.commit()

    finally:
        db.close()

        # Partial jobs retain the video
        # so /retry can actually process it again.
        if status != "partial" and os.path.exists(file_path):
            os.remove(file_path)

        if tmp_json_path and os.path.exists(tmp_json_path):
            os.remove(tmp_json_path)

        if tmp_csv_path and os.path.exists(tmp_csv_path):
            os.remove(tmp_csv_path)


@router.post(
    "/upload",
    response_model=UploadResponse,
)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=("Invalid video format. " "Accepted formats: " ".mp4, .avi, .mov"),
        )

    os.makedirs(
        UPLOAD_DIR,
        exist_ok=True,
    )

    filename = f"{uuid.uuid4()}{ext}"

    file_path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail=("Uploaded video is empty"),
            )

        with open(
            file_path,
            "wb",
        ) as destination:

            destination.write(contents)

        job = Job(
            user_id=uuid.UUID(current_user["sub"]),
            status="processing",
            video_path=file_path,
            progress=0,
            started_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )

        db.add(job)
        db.commit()
        db.refresh(job)

        background_tasks.add_task(
            process_video,
            str(job.job_id),
            file_path,
        )

        return {
            "job_id": job.job_id,
            "status": job.status,
            "created_at": (job.created_at),
        }

    except HTTPException:
        if os.path.exists(file_path):
            os.remove(file_path)

        raise

    except Exception as exc:
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail=("Internal server error " "while uploading video: " f"{exc}"),
        ) from exc
