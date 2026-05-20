import sys
import uuid
import shutil
import subprocess
from fastapi import APIRouter, UploadFile, File, HTTPException
import config

router = APIRouter()


@router.post("/formation")
async def formation_analysis(
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
    output_video = config.OUTPUTS_DIR / f"{job_id}_formation.mp4"

    with open(video_path, "wb") as f:
        shutil.copyfileobj(video.file, f)
    with open(json_path, "wb") as f:
        shutil.copyfileobj(tracking_json.file, f)

    try:
        result = subprocess.run(
            [
                sys.executable,
                str(config.FORMATION_SCRIPT_DIR / "formation_visualizer_cli.py"),
                "--input_video", str(video_path),
                "--input_tracking", str(json_path),
                "--output_video", str(output_video),
                "--no_display"
            ],
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode != 0:
            raise Exception(result.stderr or result.stdout)

        return {
            "status": "success",
            "video_url": f"/outputs/{output_video.name}"
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Formation analysis timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        video_path.unlink(missing_ok=True)
        json_path.unlink(missing_ok=True)
