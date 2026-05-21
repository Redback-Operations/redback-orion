import sys
import uuid
import json
import shutil
import argparse
from fastapi import APIRouter, UploadFile, File, HTTPException
import config

sys.path.insert(0, str(config.JERSEY_COLOR_SCRIPT_DIR))
from color_detection_cli import run_pipeline

router = APIRouter()


@router.post("/jersey_color")
async def jersey_color(
    video: UploadFile = File(...),
    tracking_json: UploadFile = File(...)
):
    if not video.filename.lower().endswith((".mp4", ".avi", ".mov")):
        raise HTTPException(status_code=400, detail="Invalid file type. Use .mp4, .avi or .mov")
    if not tracking_json.filename.lower().endswith(".json"):
        raise HTTPException(status_code=400, detail="tracking_json must be a .json file")

    job_id = str(uuid.uuid4())
    video_path = config.UPLOADS_DIR / f"{job_id}_{video.filename}"
    json_path = config.UPLOADS_DIR / f"{job_id}_tracking.json"
    output_folder = config.OUTPUTS_DIR / job_id
    output_folder.mkdir(exist_ok=True)

    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)
    with open(json_path, "wb") as f:
        shutil.copyfileobj(tracking_json.file, f)

    try:
        args = argparse.Namespace(
            input_video=str(video_path),
            tracking_json=str(json_path),
            output_folder=str(output_folder),
            clusters=3,
            process_every=1,
            min_box_width=10,
            min_box_height=20,
            min_samples_per_track=3,
            pixel_to_meter=0.1,
            max_speed_kmh=40,
            no_display=True
        )
        run_pipeline(args)

        json_out = next(output_folder.glob("*_clustered.json"))
        video_out = next(output_folder.glob("*_clustered.mp4"))
        csv_out = next(output_folder.glob("*_metrics.csv"))

        with open(json_out) as f:
            result_data = json.load(f)

        return {
            "status": "success",
            **result_data,
            "video_url": f"/outputs/{job_id}/{video_out.name}",
            "csv_url": f"/outputs/{job_id}/{csv_out.name}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        video_path.unlink(missing_ok=True)
        json_path.unlink(missing_ok=True)
