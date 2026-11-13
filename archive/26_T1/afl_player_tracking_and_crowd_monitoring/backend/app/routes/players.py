import os
import uuid
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import UPLOAD_DIR
from app.services.player_client import get_player_data
from app.database import get_db
from app.models import Player
from app.schemas.player import PlayerCreate, PlayerResponse


router = APIRouter(prefix="/api", tags=["Players"])


ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov"}
ALLOWED_MIME_TYPES = {
    "video/mp4",
    "video/x-msvideo",
    "video/quicktime",
}


# ============================================================
# PLAYER TRACKING
# Existing functionality preserved
# ============================================================

@router.post("/players")
async def run_player_tracking(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()

    if (
        ext not in ALLOWED_EXTENSIONS
        or file.content_type not in ALLOWED_MIME_TYPES
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid video format. Accepted: .mp4, .avi, .mov",
        )

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    tmp_path = os.path.join(
        UPLOAD_DIR,
        f"tmp_{uuid.uuid4()}{ext}",
    )

    try:
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        data = await get_player_data(tmp_path)

        return {
            "status": "success",
            "data": data,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ============================================================
# PLAYER DATABASE MANAGEMENT
# Team lead integration
# ============================================================

@router.post("/player")
def create_player(
    player: PlayerCreate,
    db: Session = Depends(get_db),
):
    db_player = Player(
        name=player.name,
        team=player.team,
        position=player.position,
        photo=player.photo,
        kicks=player.kicks,
        handballs=player.handballs,
        marks=player.marks,
        tackles=player.tackles,
        goals=player.goals,
        efficiency=player.efficiency,
        age=player.age,
        height=player.height,
        weight=player.weight,
        jersey_number=player.jerseyNumber,
        inside50s=player.inside50s,
        disposals=player.disposals,
        team_logo=player.teamLogo,
        notes=player.notes,
    )

    db.add(db_player)
    db.commit()
    db.refresh(db_player)

    return {
        "message": "Player created successfully",
        "player": db_player,
    }


@router.get(
    "/players",
    response_model=list[PlayerResponse],
)
def get_players(
    db: Session = Depends(get_db),
):
    players = db.query(Player).all()

    return players


@router.delete("/player/{player_id}")
def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
):
    player = (
        db.query(Player)
        .filter(Player.id == player_id)
        .first()
    )

    if player is None:
        raise HTTPException(
            status_code=404,
            detail="Player not found",
        )

    db.delete(player)
    db.commit()

    return {
        "message": "Player deleted successfully",
        "player_id": player_id,
    }