from pydantic import BaseModel, ConfigDict
from typing import Optional
 
 
class PlayerCreate(BaseModel):
    name: str
    team: str
    position: str
 
    photo: Optional[str] = None
 
    kicks: Optional[int] = 0
    handballs: Optional[int] = 0
    marks: Optional[int] = 0
    tackles: Optional[int] = 0
    goals: Optional[int] = 0
    efficiency: Optional[int] = 75
 
    age: Optional[int] = 0
    height: Optional[str] = None
    weight: Optional[str] = None
 
    jerseyNumber: Optional[int] = 0
    inside50s: Optional[int] = 0
    disposals: Optional[int] = 0
 
    teamLogo: Optional[str] = None
    notes: Optional[str] = None
 
 
class PlayerResponse(BaseModel):
    id: int
 
    name: str
    team: str
    position: str
 
    photo: Optional[str] = None
 
    kicks: int
    handballs: int
    marks: int
    tackles: int
    goals: int
    efficiency: int
 
    age: int
    height: Optional[str] = None
    weight: Optional[str] = None
 
    jersey_number: int
    inside50s: int
    disposals: int
 
    team_logo: Optional[str] = None
    notes: Optional[str] = None
 
    model_config = ConfigDict(from_attributes=True)