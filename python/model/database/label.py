from sqlalchemy import Integer, String, Boolean, Float
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base

class Label(Base):
   __tablename__ = 'labels'
   __allow_unmapped__ = True

   id: Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
   text: Mapped[str] = mapped_column(String(256))
   color: Mapped[str] = mapped_column(String(32))
   x: Mapped[float] = mapped_column(Float)
   y: Mapped[float] = mapped_column(Float)
   z: Mapped[float] = mapped_column(Float)
   dd: Mapped[float] = mapped_column(Float, default=200.0, server_default="200.0")
   interior: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
   vw: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
   desc: Mapped[str] = mapped_column(String(256), default="N/A", server_default="N/A")
