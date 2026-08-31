from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
)


class PlayerCreate(BaseModel):
    name: str
    team: str
    position: str

    photo: Optional[str] = None

    kicks: int = 0
    handballs: int = 0
    marks: int = 0
    tackles: int = 0
    goals: int = 0

    efficiency: float = 0

    age: int = 0

    height: Optional[str] = None
    weight: Optional[str] = None

    jerseyNumber: int = 0
    inside50s: int = 0
    disposals: int = 0

    teamLogo: Optional[str] = None
    notes: Optional[str] = None


class PlayerResponse(PlayerCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
