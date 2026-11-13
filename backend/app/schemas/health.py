from pydantic import BaseModel

class HealthResponse(BaseModel):
    gateway: str
    player_service: str
    crowd_service: str