from pydantic import BaseModel as PydanticModel

from .item_data import ItemData

class Item(PydanticModel):
   id: int
   name: str 
   max_amount: int
   min_price: int
   max_price: int
   volume: int
   sellable: bool 
   droppable: bool
   is_stackable: bool 
   data: ItemData | None
