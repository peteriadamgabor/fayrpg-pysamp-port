from pydantic import BaseModel as PydanticModel

from .fuel_type import FuelType

class VehicleModel(PydanticModel):
   id: int
   name: str
   real_name: str
   seats: int
   price: int
   trunk_capacity: int
   color_number: int
   tank_capacity: int
   consumption: int
   max_speed: int
   hood: bool
   airbag: bool
   #allowed_fuel_types: list[FuelType]