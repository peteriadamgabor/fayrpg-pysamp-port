from pydantic import BaseModel as PydanticModel

class Skin(PydanticModel):
    id: int
    description: str
    price: int
    sex: bool
    dl_id: int | None
