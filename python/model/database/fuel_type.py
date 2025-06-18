from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION

from .base import Base

class FuelType(Base):
   __tablename__ = 'fuel_types'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   name: Mapped[str] = mapped_column(String)
   code: Mapped[str] = mapped_column(String, unique=True, nullable=False)

   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
         defaults = [
                     {"name": "Benzin",         "code": "B" },
                     {"name": "Dízel",          "code": "D" },
                     {"name": "Kerozin",        "code": "K" },
                     {"name": "Elektromosság",  "code": "E" },
                     {"name": "Autógáz",        "code": "L" },
                    ]

         for default in defaults:
             if not session.scalars(select(FuelType).where(FuelType.code == default["code"])).one_or_none():
                 session.add(cls(**default))