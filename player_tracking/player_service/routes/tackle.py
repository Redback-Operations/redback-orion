import uuid
import json
import shutil
import pandas as pd
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException
import config

router = APIRouter()

DIST_THRESHOLD = 100
MIN_INTERACTIONS = 8
MIN_PLAYERS = 4
DENSITY_THRESHOLD = 1.2
MIN_EVENT_LENGTH = 5
MAX_FRAME_GAP = 10


def cluster_score(group):
    players = group[["cx", "cy"]].values
    score = 0
    for i in range(len(players)):
        for j in range(i + 1, len(players)):
            if np.linalg.norm(players[i] - players[j]) < DIST_THRESHOLD:
                score += 1
    return score


def group_frames(frames, max_gap=3):
    if not frames:
        return []
    frames = sorted(frames)
    grouped = []
    current = [frames[0]]
    for f in frames[1:]:
        if f <= current[-1] + max_gap:
            current.append(f)
        else:
            grouped.append(current)
            current = [f]
    grouped.append(current)
    return grouped


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
        df = pd.read_csv(csv_path)

        required = {"frame_id", "player_id", "cx", "cy", "x1", "y1", "x2", "y2", "timestamps_s"}
        missing = required - set(df.columns)
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing columns in CSV: {missing}")

        results = []
        for frame_id, group in df.groupby("frame_id"):
            num_players = group["player_id"].nunique()
            if num_players < MIN_PLAYERS:
                continue
            score = cluster_score(group)
            density_ratio = score / (num_players + 1)
            if score >= MIN_INTERACTIONS and density_ratio > DENSITY_THRESHOLD:
                results.append({
                    "frame_id": int(frame_id),
                    "timestamp_s": float(group["timestamps_s"].mean()),
                    "cluster_score": int(score),
                    "density_ratio": float(density_ratio),
                    "players": int(num_players),
                    "x_min": float(group["x1"].min()),
                    "y_min": float(group["y1"].min()),
                    "x_max": float(group["x2"].max()),
                    "y_max": float(group["y2"].max())
                })

        frame_df = pd.DataFrame(results)
        frame_df.to_csv(output_csv, index=False)

        events_output = []
        if not frame_df.empty:
            tackle_events = group_frames(frame_df["frame_id"].tolist(), MAX_FRAME_GAP)
            for idx, event_frames in enumerate(tackle_events, start=1):
                if len(event_frames) < MIN_EVENT_LENGTH:
                    continue
                eg = df[df["frame_id"].isin(event_frames)]
                fd = frame_df[frame_df["frame_id"].isin(event_frames)]
                avg_score = fd["cluster_score"].mean()
                events_output.append({
                    "event_id": idx,
                    "event_type": "multi_player_tackle",
                    "start_frame": int(event_frames[0]),
                    "end_frame": int(event_frames[-1]),
                    "start_time_s": float(eg["timestamps_s"].min()),
                    "end_time_s": float(eg["timestamps_s"].max()),
                    "duration_frames": int(event_frames[-1] - event_frames[0] + 1),
                    "players_involved": int(eg["player_id"].nunique()),
                    "cluster_score": float(avg_score),
                    "bounding_box": {
                        "x_min": float(eg["x1"].min()),
                        "y_min": float(eg["y1"].min()),
                        "x_max": float(eg["x2"].max()),
                        "y_max": float(eg["y2"].max())
                    },
                    "confidence": round(min(avg_score / 15, 1.0), 2)
                })

        final = {"video_id": job_id, "events": events_output}
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
