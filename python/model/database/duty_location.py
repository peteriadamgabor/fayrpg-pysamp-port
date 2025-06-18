from sqlalchemy import Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .base import Base

class DutyLocation(Base):
   __tablename__ = 'fraction_duty_locations'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   fraction_id: Mapped[int] = mapped_column(ForeignKey("fractions.id"))
   fraction: Mapped["Fraction"] = relationship("Fraction", back_populates="duty_points")
   x: Mapped[float] = mapped_column(Float)
   y: Mapped[float] = mapped_column(Float)
   z: Mapped[float] = mapped_column(Float)
   size: Mapped[float] = mapped_column(Float)
   interior: Mapped[int] = mapped_column(Integer)
   virtual_word: Mapped[int] = mapped_column(Integer)
   in_game_id: Mapped[int] = mapped_column(Integer)
