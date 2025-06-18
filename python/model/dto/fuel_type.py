from pydantic import BaseModel as PydanticModel

class FuelType(PydanticModel):
   id: int
   name: str
   code: str
