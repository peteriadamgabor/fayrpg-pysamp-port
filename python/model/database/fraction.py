from sqlalchemy import Integer, String, Boolean, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION

from .base import Base
from .skin import Skin
from .duty_location import DutyLocation
from .division import Division

class Fraction(Base):
   __tablename__ = 'fractions'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   name: Mapped[str] = mapped_column(String)
   acronym: Mapped[str] = mapped_column(String, unique=True, nullable=False)
   duty_everywhere: Mapped[bool] = mapped_column(Boolean)
   skins: Mapped[list["Skin"]] = relationship("Skin", secondary="fraction_skins")
   divisions: Mapped[list["Division"]] = relationship("Division", back_populates="fraction")
   duty_points: Mapped[list["DutyLocation"]] = relationship("DutyLocation", back_populates="fraction")
   ranks: Mapped[list["Rank"]] = relationship("Rank", back_populates="fraction", order_by="Rank.order") # type: ignore
   frequencies: Mapped[list["Frequency"]] = relationship("Frequency", back_populates="fraction") # type: ignore
   type: Mapped[int] = mapped_column(Integer)
   
   
   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
         defaults = [
                     {"name": "Országos Rendőr-Főkapitányság",             "acronym": "ORFK",   "duty_everywhere": False , "type": 1 },
                     {"name": "Országos Mentőszolgálat",                   "acronym": "OMSZ",   "duty_everywhere": False , "type": 2 },
                     {"name": "Országos Katasztrófavédelmi Főigazgatóság", "acronym": "OKF",    "duty_everywhere": False , "type": 3 },
                     {"name": "Állami Önkormányzat",                       "acronym": "GOV",    "duty_everywhere": False , "type": 4 },
                     {"name": "Nemzeti Média- és Hírközlési Hatóság",      "acronym": "NMHH",   "duty_everywhere": False , "type": 5 }
                    ]

         for default in defaults:
             if not session.scalars(select(Fraction).where(Fraction.acronym == default["acronym"])).one_or_none():
                 session.add(cls(**default))
