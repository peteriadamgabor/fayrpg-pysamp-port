from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base

class ItemData(Base):
   __tablename__ = 'item_data'

   item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), primary_key=True)
   item: Mapped["Item"] = relationship("Item", back_populates="data")
   weapon_id: Mapped[int] = mapped_column(Integer)
   type: Mapped[int] = mapped_column(Integer)
   heal: Mapped[int] = mapped_column(Integer)
