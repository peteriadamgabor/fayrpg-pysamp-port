from sqlalchemy import Boolean, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base

class Division(Base):
   __tablename__ = 'divisions'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   fraction_id: Mapped[int] = mapped_column(ForeignKey("fractions.id"))
   fraction: Mapped["Fraction"] = relationship("Fraction", back_populates="divisions")
   ranks: Mapped[list["Rank"]] = relationship("Rank", back_populates="division")
   name: Mapped[str] = mapped_column(String)
   acronym: Mapped[str] = mapped_column(String)
   is_leader: Mapped[bool] = mapped_column(Boolean)
   is_recruit:  Mapped[bool] = mapped_column(Boolean)

