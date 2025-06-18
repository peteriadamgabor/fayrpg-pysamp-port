from sqlalchemy import Integer, String, Float, ForeignKey

from sqlalchemy.orm import relationship, mapped_column, Mapped

from .base import Base
from .business_type import BusinessType

from python.database import transactional_session
from python.server.database import MAIN_SESSION

class Interior(Base):
   __tablename__ = 'interiors'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   name: Mapped[str] = mapped_column(String)
   x: Mapped[float] = mapped_column(Float)
   y: Mapped[float] = mapped_column(Float)
   z: Mapped[float] = mapped_column(Float)
   a: Mapped[float] = mapped_column(Float)
   interior: Mapped[int] = mapped_column(Integer)
   business_type_id: Mapped[int] = mapped_column(ForeignKey("business_types.id"), nullable=True)
   business_type: Mapped["BusinessType"] = relationship("BusinessType")
   price: Mapped[int] = mapped_column(Integer)


   @classmethod
   def create(cls, x: float, y: float, z: float, a: float, interior: int, *args) -> None:
      with transactional_session(MAIN_SESSION) as session:
         session.add(cls(name=" ".join(args), x = x, y = y, z = z, a = a, interior = interior))
