from pydantic import BaseModel as PydanticModel

from .item import Item

class ShopItem(PydanticModel):
    business_id: int
    item_id: int
    price: int
    amount: int
    give_amount: int
