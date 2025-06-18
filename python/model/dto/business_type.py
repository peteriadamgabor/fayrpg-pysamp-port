from pydantic import BaseModel as PydanticModel

class BusinessType(PydanticModel):
    id: int
    name: str
    code: str
