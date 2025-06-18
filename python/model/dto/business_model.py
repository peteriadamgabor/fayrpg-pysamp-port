from pydantic import BaseModel as PydanticModel

from .interior import Interior
from .player import Player
from .business_type import BusinessType

class BusinessModel(PydanticModel):
    id: int
    in_game_id: int
    business_type: BusinessType 
    interior: Interior
    owner: Player
    price: int
    name: str
    x: float
    y: float
    z: float
    a: float
    locked: bool
    company_chain: int
    is_illegal: bool
