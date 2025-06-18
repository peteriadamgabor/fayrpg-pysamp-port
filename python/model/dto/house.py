from pydantic import BaseModel as PydanticModel
from datetime import datetime

from .player import Player
from .house_type import HouseType 

class House(PydanticModel):
   id: int
   entry_x: float
   entry_y: float
   entry_z: float
   angle: float
   type: int
   locked: bool | None
   price: int
   rent_date: datetime | None
   owner: Player | None
   house_type: HouseType
   is_spawn: bool | None