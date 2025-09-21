from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from track import Tracking
from afl_heatmap import run_pipeline
import shutil
import os
import uuid
import math
import json
from pathlib import Path


app = FastAPI(title="AFL Player Tracking Microservice")

# Base directory of this file (tracking_code/)
BASE_DIR = Path(__file__).resolve().parent

# Either use environment variable or fallback to local best.pt
MODEL_PATH = os.getenv("MODEL_PATH", BASE_DIR / "best.pt")

tracking_model = Tracking(model_path=str(MODEL_PATH), confidence_threshold=0.3)

# Directories
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
ANALYTICS_DIR = "analytics"
HEATMAP_DIR = "heatmaps"

for d in [UPLOAD_DIR, OUTPUT_DIR, ANALYTICS_DIR, HEATMAP_DIR]:
    os.makedirs(d, exist_ok=True)

# ✅ Mount static folders
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
app.mount("/analytics", StaticFiles(directory=ANALYTICS_DIR), name="analytics")
app.mount("/heatmaps", StaticFiles(directory=HEATMAP_DIR), name="heatmaps")


# ---------------------------
# Postprocess utils
# ---------------------------
def postprocess_tracking(results: dict, file_id: str, base_url: str, label: str) -> dict:
    """Convert raw tracking results into compact analytics JSON with heatmap links."""
    players_data = {}

    for frame in results["tracking_results"]:
        timestamp = frame["timestamp"]
        for player in frame["players"]:
            if player.get("confidence", 0) < 0.5:
                continue

            pid = player["player_id"]
            center = player["center"]

            if pid not in players_data:
                players_data[pid] = {"coords": [], "timestamps": []}

            players_data[pid]["coords"].append((center["x"], center["y"]))
            players_data[pid]["timestamps"].append(timestamp)

    processed_players = []
    for pid, pdata in players_data.items():
        coords = pdata["coords"]
        times = pdata["timestamps"]
        if len(coords) < 2:
            continue

        # Smooth coords
        smoothed = []
        for i in range(len(coords)):
            start = max(0, i - 4)
            x_avg = sum(c[0] for c in coords[start:i + 1]) / (i - start + 1)
            y_avg = sum(c[1] for c in coords[start:i + 1]) / (i - start + 1)
            smoothed.append((x_avg, y_avg))

        # Distance & speeds
        total_distance_m = 0.0
        speeds = []
        for i in range(1, len(smoothed)):
            x1, y1 = smoothed[i - 1]
            x2, y2 = smoothed[i]
            dist_px = math.dist((x1, y1), (x2, y2))
            dist_m = dist_px * 0.05
            dt = times[i] - times[i - 1]
            if dt > 0 and dist_m / dt <= 8.0:  # outlier rejection
                total_distance_m += dist_m
                speeds.append(dist_m / dt)

        duration = times[-1] - times[0]
        avg_speed_m_s = total_distance_m / duration if duration > 0 else 0
        max_speed_m_s = max(speeds) if speeds else 0

        processed_players.append({
            "id": pid,
            "distance_m": round(total_distance_m, 2),
            "average_speed_m_s": round(avg_speed_m_s, 2),
            "average_speed_kmh": round(avg_speed_m_s * 3.6, 2),
            "max_speed_m_s": round(max_speed_m_s, 2),
            "max_speed_kmh": round(max_speed_m_s * 3.6, 2),
            "heatmap": f"{base_url}/heatmaps/{label}/per_id/id_{pid}.png"
        })

    # Add zone-level heatmaps
    zones = {
        "back_50": f"{base_url}/heatmaps/{label}/zones/back_50.png",
        "midfield": f"{base_url}/heatmaps/{label}/zones/midfield.png",
        "forward_50": f"{base_url}/heatmaps/{label}/zones/forward_50.png"
    }

    # ✅ Add overall team heatmap
    team_heatmap = f"{base_url}/heatmaps/{label}/overall/overall.png"

    return {
        "video_info": results["video_info"],
        "players": processed_players,
        "zones": zones,
        "team_heatmap": team_heatmap
    }


# ---------------------------
# API Endpoint
# ---------------------------
@app.post("/track")
async def track_video(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())
        input_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        output_path = os.path.join(OUTPUT_DIR, f"{file_id}_tracked.mp4")

        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # ✅ Run tracking
        raw_results = tracking_model(
            video_path=input_path,
            output_video=output_path,
            save_csv=True
        )

        # Paths
        csv_path = os.path.join(
            OUTPUT_DIR, f"{file_id}_{file.filename.rsplit('.',1)[0]}_tracking.csv"
        )
        json_path = os.path.join(ANALYTICS_DIR, f"{file_id}_analytics.json")
        label = f"tracking_{file_id}"

        # ✅ Run heatmap pipeline
        run_pipeline([(csv_path, label)], out_root=HEATMAP_DIR, sigma=2.0)

        # ✅ Postprocess analytics with links
        base_url = "http://127.0.0.1:8001"
        analytics = postprocess_tracking(raw_results, file_id, base_url, label)

        # Save analytics JSON
        with open(json_path, "w") as jf:
            json.dump(analytics, jf, indent=2)

        # ✅ Build final response
        return JSONResponse(content={
            "status": "success",
            "upload_id": file_id,
            "files": {
                "input_video": f"{base_url}/uploads/{file_id}_{file.filename}",
                "output_video": f"{base_url}/outputs/{file_id}_tracked.mp4",
                "tracking_csv": f"{base_url}/outputs/{file_id}_{file.filename.rsplit('.',1)[0]}_tracking.csv",
                "analytics_json": f"{base_url}/analytics/{file_id}_analytics.json",
                "heatmaps_dir": f"{base_url}/heatmaps/{label}/"
            },
            "analytics": analytics
        })

    except Exception as e:
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)


@app.get("/")
def root():
    return {"message": "AFL Player Tracking Microservice is running 🚀"}
