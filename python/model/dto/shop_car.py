from pydantic import BaseModel as PydanticModel

from .vehicle_model import VehicleModel

class ShopCar(PydanticModel):
    business_id: int
    vehicle_model_id: int
    #vehicle_model: VehicleModel
