from pydantic import BaseModel as PydanticModel

class TelCoTower(PydanticModel):
   id: int
   x: float
   y: float
   radius: float
   in_game_id: int
