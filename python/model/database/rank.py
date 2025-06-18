from sqlalchemy import Integer, String, ForeignKey, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base
from .fraction import Fraction
from .division import Division
from python.database import transactional_session
from python.server.database import MAIN_SESSION


class Rank(Base):
   __tablename__ = 'ranks'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   order: Mapped[int] = mapped_column(Integer, nullable=False)
   fraction_id: Mapped[int] = mapped_column(ForeignKey("fractions.id"), nullable=False)
   fraction: Mapped["Fraction"] = relationship("Fraction", back_populates="ranks")
   division_id: Mapped[int] = mapped_column(ForeignKey("divisions.id"), nullable=True)
   division: Mapped["Division"] = relationship("Division", back_populates="ranks")
   name: Mapped[str] = mapped_column(String)
   code: Mapped[str] = mapped_column(String, unique=True, nullable=False)


   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:

         orfk_id: int = session.scalars(select(Fraction).where(Fraction.acronym == "ORFK")).one().id

         orfk_defaults = [
                     {"name": "Kadét",           "code": "KK", "order": 0,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Õrmester",        "code": "ORM", "order": 1,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Törzsõrmester",   "code": "TORM", "order": 2,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Fõtörzsõrmester", "code": "FTORM", "order": 3,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Zászlós",         "code": "ZLS", "order": 4,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Törzszászlós",    "code": "TZLS", "order": 5,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Fõtörzszászlós",  "code": "FTZLS", "order": 6,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Hadnagy",         "code": "HDGY", "order": 7,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Fõhadnagy",       "code": "FHDGY", "order": 8,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Százados",        "code": "SZDS", "order": 9,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Õrnagy",          "code": "ORGY", "order": 10,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Alezredes",       "code": "ALEZ", "order": 11,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Ezredes",         "code": "EZDS", "order": 12,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Dandártábornok",  "code": "DDTDK", "order": 13,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Vezérõrnagy",     "code": "VORGY", "order": 14,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Altábornagy",     "code": "ALTBGY", "order": 15,  "fraction_id": orfk_id, "division_id": None },
                     {"name": "Vezérezredes",    "code": "VEZDS", "order": 16, "fraction_id": orfk_id, "division_id": None },
         ]

         for default in orfk_defaults:
             if not session.scalars(select(Rank).where(Rank.code == default["code"])).one_or_none():
                 session.add(cls(**default))
