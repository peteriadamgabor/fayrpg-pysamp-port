from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import insert as pg_insert

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION

from .base import Base
from .fraction import Fraction

class Frequency(Base):
   __tablename__ = 'frequencies'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   number: Mapped[int] = mapped_column(Integer)
   password: Mapped[int] = mapped_column(Integer)
   fraction_id: Mapped[int] = mapped_column(ForeignKey("fractions.id"))
   fraction: Mapped["Fraction"] = relationship("Fraction", back_populates="frequencies")
