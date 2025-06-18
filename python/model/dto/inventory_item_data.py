from pydantic import BaseModel as PydanticModel

from .vehicle import Vehicle

class InventoryItemData(PydanticModel):
    id: int
    vehicle: Vehicle | None
