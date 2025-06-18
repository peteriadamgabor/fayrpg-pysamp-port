from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base

class Teleport(Base):
   __tablename__ = 'teleports'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   from_x: Mapped[float] = mapped_column(Float)
   from_y: Mapped[float] = mapped_column(Float)
   from_z: Mapped[float] = mapped_column(Float)
   from_angel: Mapped[float] = mapped_column(Float)
   from_interior: Mapped[int] = mapped_column(Integer)
   from_vw: Mapped[int] = mapped_column(Integer)
   radius: Mapped[float] = mapped_column(Float)
   to_x: Mapped[float] = mapped_column(Float)
   to_y: Mapped[float] = mapped_column(Float)
   to_z: Mapped[float] = mapped_column(Float)
   to_angel: Mapped[float] = mapped_column(Float)
   to_interior: Mapped[int] = mapped_column(Integer)
   to_vw: Mapped[int] = mapped_column(Integer)
   description: Mapped[str] = mapped_column(String)

