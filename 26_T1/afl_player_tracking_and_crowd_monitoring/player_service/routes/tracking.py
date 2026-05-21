import sys
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
import config

sys.path.insert(0, str(config.TRACKING_SCRIPT_DIR))
from track import Tracking

router = APIRouter()
_tracker = None


def get_tracker():
    global _tracker
    if _tracker is None:
        _tracker = Tracking(model_path=str(config.MODEL_PATH), confidence_threshold=0.3)
    return _tracker


@router.post("/tracking")
async def player_tracking(video: UploadFile = File(...)):
    if not video.filename.lower().endswith((".mp4", ".avi", ".mov")):
        raise HTTPException(status_code=400, detail="Invalid file type. Use .mp4, .avi or .mov")

    job_id = str(uuid.uuid4())
    video_path = config.UPLOADS_DIR / f"{job_id}_{video.filename}"
    output_video = config.OUTPUTS_DIR / f"{job_id}_tracking.mp4"

    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)

    try:
        tracker = get_tracker()
        results = tracker(
            video_path=str(video_path),
            output_video=str(output_video),
            save_json=False
        )
        return {
            "status": "success",
            "video_info": results["video_info"],
            "tracking_results": results["tracking_results"],
            "video_url": f"/outputs/{output_video.name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        video_path.unlink(missing_ok=True)
