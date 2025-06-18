from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from python.model.database import Business

from .base import Base
from .item_data import ItemData

class RestaurantMenu(Base):
   __tablename__ = 'restaurant_menus'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   name: Mapped[str] = mapped_column(String)
   price: Mapped[int] = mapped_column(Integer)
   business_id: Mapped[int] = mapped_column(ForeignKey("business.id"), nullable=True)
   business: Mapped["Business"] = relationship("Business")
   execute: Mapped[str] = mapped_column(String)

