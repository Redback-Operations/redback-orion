import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
import config
from tracks import get_tracks
from analysis_pipeline.tracking_json import to_legacy_json

router = APIRouter()


def run_tracking(video_path: Path, tracks_dir: Path, key: str) -> dict:
    """Track players with the analysis pipeline and return the /tracking response."""
    from analysis_pipeline.detect_and_track import run

    info = run(
        video_path,
        model_path=config.ensure_model(),
        tracker=config.TRACKER_CONFIG,
        conf=config.TRACKING_CONFIDENCE,
        out_dir=tracks_dir,
        stem=key,
    )
    result = to_legacy_json(info["csv"], info)
    result["video_url"] = f"/outputs/{tracks_dir.name}/{info['video'].name}"
    return result


@router.post("/tracking")
async def player_tracking(video: UploadFile = File(...)):
    if not video.filename.lower().endswith((".mp4", ".avi", ".mov")):
        raise HTTPException(status_code=400, detail="Invalid file type. Use .mp4, .avi or .mov")

    job_id = str(uuid.uuid4())
    video_path = config.UPLOADS_DIR / f"{job_id}_{Path(video.filename).name}"

    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)

    try:
        return get_tracks(video_path, config.TRACKS_DIR, run_tracking)
    except config.DownloadError as e:
        raise HTTPException(status_code=503, detail=f"Tracking model unavailable. {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        video_path.unlink(missing_ok=True)
