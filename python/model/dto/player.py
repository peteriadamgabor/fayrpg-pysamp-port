import datetime
from pydantic import BaseModel as PydanticModel


class Player(PydanticModel):
    id: int
    name: str
    sex: int
    birthdate: datetime.date
