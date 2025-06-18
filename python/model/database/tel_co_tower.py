from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base

class TelCoTower(Base):
   __tablename__ = 'telcotowers'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   x: Mapped[float] = mapped_column(Float)
   y: Mapped[float] = mapped_column(Float)
   radius: Mapped[float] = mapped_column(Float)
   in_game_id: Mapped[int] = mapped_column(Integer)
