import uuid
import json
import shutil
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException
import config
from analysis_pipeline.tackle_detection import detect_tackles

router = APIRouter()


@router.post("/tackle")
async def tackle_detection(tracking_csv: UploadFile = File(...)):
    if not tracking_csv.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="tracking_csv must be a .csv file")

    job_id = str(uuid.uuid4())
    csv_path = config.UPLOADS_DIR / f"{job_id}_tracking.csv"
    output_csv = config.OUTPUTS_DIR / f"{job_id}_tackle_frames.csv"
    output_json = config.OUTPUTS_DIR / f"{job_id}_tackle_events.json"

    with open(csv_path, "wb") as f:
        shutil.copyfileobj(tracking_csv.file, f)

    try:
        try:
            frame_df, events = detect_tackles(pd.read_csv(csv_path))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        frame_df.to_csv(output_csv, index=False)
        final = {"video_id": job_id, "events": events}
        with open(output_json, "w") as f:
            json.dump(final, f, indent=2)

        return {
            "status": "success",
            **final,
            "csv_url": f"/outputs/{output_csv.name}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        csv_path.unlink(missing_ok=True)
