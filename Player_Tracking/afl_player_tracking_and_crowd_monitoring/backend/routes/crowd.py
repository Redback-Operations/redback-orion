from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
import cv2, requests, shutil

from routes.auth import get_current_user
from storage import get_upload, save_crowd_analysis, get_crowd_analysis,save_inference,get_inferences

router = APIRouter(tags=["Crowd Inference"])

CROWD_API_URL = "https://5c18a59a4255.ngrok-free.app"

# -------------------------------
# Helpers & directories
# -------------------------------
def _resolve_upload_abs_path(rec: dict) -> Path:
    """Resolve upload record relative path into absolute backend path."""
    backend_dir = Path(__file__).resolve().parents[1]  # backend/
    return (backend_dir / str(rec["path"]).lstrip("/\\")).resolve()

STATIC_DIR = Path("static")
CROWD_ROOT = STATIC_DIR / "crowd"
CROWD_ROOT.mkdir(parents=True, exist_ok=True)

def _make_static_url(path: Path) -> str:
    """Convert a saved file path into a static URL."""
    return f"http://127.0.0.1:8000/static/{path.relative_to(STATIC_DIR).as_posix()}"


# -------------------------------
# Crowd Inference
# -------------------------------
@router.post("/inference/crowd/{upload_id}", summary="Run crowd analysis on a video")
def run_crowd_analysis(
    upload_id: str,
    user_id: int = Depends(get_current_user),
):
    # 🔹 Validate upload
    upload = get_upload(upload_id)
    if not upload or upload["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized or upload not found")

    abs_path = _resolve_upload_abs_path(upload)
    if not abs_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")

    # 🔹 Mark job as "Analyzing..."
    inference = save_inference(
        upload_id=upload_id,
        user_id=user_id,
        task="crowd",
        status="Analyzing...",
        payload={}
    )

    # 🔹 Prepare directories
    upload_dir = CROWD_ROOT / upload_id
    frames_dir = upload_dir / "frames"
    heatmaps_dir = upload_dir / "heatmaps"
    frames_dir.mkdir(parents=True, exist_ok=True)
    heatmaps_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(abs_path))
    frame_num = 0
    frames_detected = 0
    frames_analyzed = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_num % 30 == 0:  # sample every 30th frame
                frames_analyzed += 1
                frame_path = frames_dir / f"frame_{frame_num}.jpg"
                cv2.imwrite(str(frame_path), frame)

                with open(frame_path, "rb") as f:
                    files = {"file": (frame_path.name, f, "image/jpeg")}
                    resp = requests.post(CROWD_API_URL, files=files)

                if resp.status_code == 200:
                    heatmap_path = heatmaps_dir / f"heatmap_{frame_num}.png"
                    with open(heatmap_path, "wb") as out:
                        out.write(resp.content)

                    count = int(resp.headers.get("People-Count", 0))

                    if count > 0:
                        # 🔹 Save per-frame detection
                        save_crowd_analysis(
                            upload_id=upload_id,
                            frame_number=frame_num,
                            people_count=count,
                            frame_image_path=_make_static_url(frame_path),
                            heatmap_image_path=_make_static_url(heatmap_path),
                        )
                        frames_detected += 1
                    else:
                        # cleanup unused files if no people detected
                        frame_path.unlink(missing_ok=True)
                        heatmap_path.unlink(missing_ok=True)
                else:
                    print(f"❌ Crowd API failed for frame {frame_num}")

            frame_num += 1

        cap.release()

        results = get_crowd_analysis(upload_id)

        if frames_detected == 0:
            shutil.rmtree(upload_dir, ignore_errors=True)
            inference = save_inference(
                upload_id=upload_id,
                user_id=user_id,
                task="crowd",
                status="Failed",
                payload={
                    "frames_analyzed": frames_analyzed,
                    "frames_detected": 0,
                    "message": "No people detected"
                }
            )
            return {
                "status": "no-heatmaps",
                "message": "No people detected in this video. No heatmaps generated.",
                "upload_id": upload_id,
                "inference": inference,
                "results": []
            }

        # ✅ Update inference → Completed
        inference = save_inference(
            upload_id=upload_id,
            user_id=user_id,
            task="crowd",
            status="Completed",
            payload={
                "frames_analyzed": frames_analyzed,
                "frames_detected": frames_detected
            }
        )

        return {
            "status": "success",
            "upload_id": upload_id,
            "inference": inference,
            "frames_analyzed": frames_analyzed,
            "frames_detected": frames_detected,
            "results": results
        }

    except Exception as e:
        inference = save_inference(
            upload_id=upload_id,
            user_id=user_id,
            task="crowd",
            status="Failed",
            payload={"error": str(e)}
        )
        raise HTTPException(status_code=500, detail=f"crowd analysis failed: {str(e)}")
