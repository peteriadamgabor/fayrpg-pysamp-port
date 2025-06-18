from pydantic import BaseModel as PydanticModel


from .item import Item
from .inventory_item_data import InventoryItemData
from .player import Player

class InventoryItem(PydanticModel):
   id: int
   item: Item
   inventory_item_data: InventoryItemData | None
   amount: int
   worn: bool
   dead: bool
