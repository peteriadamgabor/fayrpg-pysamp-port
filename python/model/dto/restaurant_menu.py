from pydantic import BaseModel as PydanticModel

class RestaurantMenu(PydanticModel):
   id: int
   name: str
   price: int
   execute: str
