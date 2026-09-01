import os
import uuid
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import UPLOAD_DIR
from app.services.player_client import get_player_data

router = APIRouter(prefix="/api", tags=["Players"])

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov"}
ALLOWED_MIME_TYPES = {"video/mp4", "video/x-msvideo", "video/quicktime"}


@router.post("/players")
async def run_player_tracking(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid video format. Accepted: .mp4, .avi, .mov")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    tmp_path = os.path.join(UPLOAD_DIR, f"tmp_{uuid.uuid4()}{ext}")
    try:
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        data = await get_player_data(tmp_path)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)