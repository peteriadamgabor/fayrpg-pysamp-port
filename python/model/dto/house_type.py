from pydantic import BaseModel as PydanticModel

class HouseType(PydanticModel):
   id: int
   enter_x: float
   enter_y: float
   enter_z: float
   angle: float
   interior: int
   description: str
   price: int
