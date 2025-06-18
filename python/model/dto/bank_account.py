from pydantic import BaseModel as PydanticModel

from .player import Player
from .business_model import BusinessModel
from .fraction import Fraction

class BankAccount(PydanticModel):
    id: int
    number: str
    password: str
    balance: float
    owner: Player
    business: BusinessModel
    fraction: Fraction
    is_default: bool
