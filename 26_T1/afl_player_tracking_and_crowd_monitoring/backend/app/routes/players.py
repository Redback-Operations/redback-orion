import os
import shutil
import uuid

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR

from app.database import get_db

from app.models import Player

from app.schemas.players import (
    PlayerCreate,
)

from app.services.player_client import (
    get_player_data,
)

router = APIRouter(tags=["Players"])


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


def _serialize_player(
    player: Player,
):
    return {
        "id": player.id,
        "name": player.name,
        "team": player.team,
        "position": player.position,
        "photo": player.photo,
        "kicks": player.kicks,
        "handballs": player.handballs,
        "marks": player.marks,
        "tackles": player.tackles,
        "goals": player.goals,
        "efficiency": player.efficiency,
        "age": player.age,
        "height": player.height,
        "weight": player.weight,
        "jerseyNumber": (player.jerseyNumber),
        "inside50s": player.inside50s,
        "disposals": player.disposals,
        "teamLogo": player.teamLogo,
        "notes": player.notes,
    }


@router.get("/api/players")
def list_players(
    db: Session = Depends(get_db),
):
    players = db.query(Player).order_by(Player.name.asc()).all()

    return {"players": [_serialize_player(player) for player in players]}


@router.post(
    "/api/players",
    status_code=201,
)
def create_player(
    payload: PlayerCreate,
    db: Session = Depends(get_db),
):
    player = Player(**payload.model_dump())

    db.add(player)
    db.commit()
    db.refresh(player)

    return _serialize_player(player)


@router.get("/players/{player_id}")
@router.get("/api/players/{player_id}")
def get_player(
    player_id: int,
    db: Session = Depends(get_db),
):
    player = db.query(Player).filter(Player.id == player_id).first()

    if not player:
        raise HTTPException(
            status_code=404,
            detail="Player not found",
        )

    return _serialize_player(player)


@router.post("/api/player-tracking")
async def run_player_tracking(
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
        ) as destination:
            shutil.copyfileobj(
                file.file,
                destination,
            )

        data = await get_player_data(tmp_path)

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
