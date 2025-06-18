from pydantic import BaseModel as PydanticModel
from .fraction import Fraction as FractionDTO

class DutyLocation(PydanticModel):
    id: int
    x: float
    y: float
    z: float
    size: float
    interior: int
    virtual_word: int
    fraction: FractionDTO
    in_game_id: int