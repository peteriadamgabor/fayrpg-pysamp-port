from pydantic import BaseModel as PydanticModel


class ItemData(PydanticModel):
   item_id: int
   weapon_id: int
   type: int
   heal: int
