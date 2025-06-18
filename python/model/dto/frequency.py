from pydantic import BaseModel as PydanticModel

from .fraction import Fraction

class Frequency(PydanticModel):
   __tablename__ = 'frequencies'
   __allow_unmapped__ = True

   id: int
   number: int
   password: int
   fraction: Fraction
