import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from app.config import (
    UPLOAD_DIR,
)

from app.services.crowd_client import (
    get_crowd_data,
)

router = APIRouter(
    prefix="/api",
    tags=["Crowd"],
)


ALLOWED_EXTENSIONS = {
    ".mp4",
    ".avi",
    ".mov",
}


ALLOWED_MIME_TYPES = {
    "video/mp4",
    "video/x-msvideo",
    "video/quicktime",
}


@router.post("/crowd")
async def run_crowd_detection(
    file: UploadFile = File(...),
):
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in ALLOWED_EXTENSIONS or file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=("Invalid video format. " "Accepted: .mp4, .avi, .mov"),
        )

    os.makedirs(
        UPLOAD_DIR,
        exist_ok=True,
    )

    tmp_path = os.path.join(
        UPLOAD_DIR,
        f"tmp_{uuid.uuid4()}{ext}",
    )

    try:
        with open(
            tmp_path,
            "wb",
        ) as file_handle:

            shutil.copyfileobj(
                file.file,
                file_handle,
            )

        data = await get_crowd_data(tmp_path)

        return {
            "status": "success",
            "data": data,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
