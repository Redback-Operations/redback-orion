import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
import config
from tracks import file_hash, get_tracks, tracks_csv_path
from routes.tracking import run_tracking


router = APIRouter()


@router.post("/path_trajectory")
async def path_trajectory(video: UploadFile = File(...)):
    if not video.filename.lower().endswith((".mp4", ".avi", ".mov")):
        raise HTTPException(status_code=400, detail="Invalid file type. Use .mp4, .avi or .mov")

    job_id = str(uuid.uuid4())
    video_path = config.UPLOADS_DIR / f"{job_id}_{Path(video.filename).name}"
    output_video = config.OUTPUTS_DIR / f"{job_id}_trajectory.mp4"
    output_json = config.OUTPUTS_DIR / f"{job_id}_trajectory.json"
    output_csv = config.OUTPUTS_DIR / f"{job_id}_player_metrics.csv"

    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)

    try:
        from analysis_pipeline.movement_metrics.config import TrackingConfig
        from analysis_pipeline.movement_metrics.video_processor import process_tracks

        # Reuse the tracks /tracking saved for this video, or run tracking now.
        key = file_hash(video_path)
        get_tracks(video_path, config.TRACKS_DIR, run_tracking, key=key)

        tracking_config = TrackingConfig(
            video_path=video_path,
            output_video_path=output_video,
            output_json_path=output_json,
            output_csv_path=output_csv,
            process_seconds=9999,
        )

        result_data = process_tracks(tracking_config, tracks_csv_path(config.TRACKS_DIR, key))
        movement_metrics = result_data.get("movement_metrics", {})

        internal_keys = {
            "video_path",
            "model_path",
            "output_video_path",
            "output_json_path",
            "output_csv_path",
        }

        return {
            "status": "success",
            **{k: v for k, v in result_data.items() if k not in internal_keys},
            "metric_mode": movement_metrics.get("metric_mode"),
            "calibration_available": movement_metrics.get("calibration_available"),
            "metrics_csv_url": f"/outputs/{output_csv.name}",
            "video_url": f"/outputs/{output_video.name}",
        }

    except config.DownloadError as e:
        raise HTTPException(status_code=503, detail=f"Tracking model unavailable. {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        video_path.unlink(missing_ok=True)
