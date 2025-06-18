from pydantic import BaseModel as PydanticModel


class Teleport(PydanticModel):

   id: int
   from_x: float
   from_y: float
   from_z: float
   from_interior: int
   from_vw: int
   radius: float
   to_x: float
   to_y: float
   to_z: float
   to_angel: float
   to_interior: int
   to_vw: int
   description: str
   in_game_id: int
