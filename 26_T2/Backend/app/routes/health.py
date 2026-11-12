import httpx
from fastapi import APIRouter
from app.schemas.health import HealthResponse
from app.config import PLAYER_SERVICE_URL, CROWD_SERVICE_URL

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    async def ping(url: str) -> str:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                r = await client.get(url)
            return "ok" if r.status_code < 500 else "error"
        except Exception:
            return "unreachable"

    player_status = await ping(f"{PLAYER_SERVICE_URL}/")
    crowd_status = await ping(f"{CROWD_SERVICE_URL}/")

    return {
        "gateway": "ok",
        "player_service": player_status,
        "crowd_service": crowd_status,
    }
