from pydantic import BaseModel as PydanticModel

from .vehicle_model import VehicleModel
from .fuel_type import FuelType

class Vehicle(PydanticModel):
   id: int
   in_game_id: int
   Vehicle_model_id: int
   model: VehicleModel
   x: float
   y: float
   z: float
   angle: float
   color_1: int
   color_2: int
   fuel_type: FuelType
   fill_type: FuelType
   fuel_level: float
   locked: bool
   health: float
   plate: str
   panels_damage: int
   doors_damage: int
   lights_damage: int
   tires_damage: int
