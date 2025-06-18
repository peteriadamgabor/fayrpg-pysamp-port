from sqlalchemy import Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base
from .item_data import ItemData
from python.database import transactional_session
from python.server.database import MAIN_SESSION


class Item(Base):
   __tablename__ = 'items'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
   max_amount: Mapped[int] = mapped_column(Integer)
   min_price: Mapped[int] = mapped_column(Integer)
   max_price: Mapped[int] = mapped_column(Integer)
   volume: Mapped[int] = mapped_column(Integer)
   sellable: Mapped[bool] = mapped_column(Boolean)
   droppable: Mapped[bool] = mapped_column(Boolean)
   is_stackable: Mapped[bool] = mapped_column(String)
   data: Mapped["ItemData"] = relationship("ItemData", back_populates="item")
   execute: Mapped[str] = mapped_column(String)
   is_usable: Mapped[bool] = mapped_column(Boolean, server_default="0", default=0)


   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
         defaults = [
            {"name": "Kalapács", "max_amount": 1, "min_price": 1_000, "max_price": 1_500, "volume": 0, "sellable": False,
              "droppable": True, "is_stackable": True, "data": None, "execute": "", "is_usable": False },

            {"name": "Csavarhúzó", "max_amount": 1, "min_price": 1_000, "max_price": 1_500, "volume": 0, "sellable": False,
             "droppable": True, "is_stackable": True, "data": None, "execute": "", "is_usable": False},

            {"name": "Ékszer", "max_amount": 1, "min_price": 500, "max_price": 1_500_000, "volume": 0, "sellable": True,
             "droppable": True, "is_stackable": True, "data": None, "execute": "", "is_usable": False},

            {"name": "Készpénz", "max_amount": 1, "min_price": 0, "max_price": 750_000, "volume": 0, "sellable": False,
             "droppable": True, "is_stackable": True, "data": None, "execute": "", "is_usable": False},

            {"name": "Laptop", "max_amount": 1, "min_price": 250_000, "max_price": 1_000_000, "volume": 0, "sellable": True,
             "droppable": True, "is_stackable": True, "data": None, "execute": "", "is_usable": False},

            {"name": "Tablet", "max_amount": 1, "min_price": 325_000, "max_price": 5500_000, "volume": 0, "sellable": True,
             "droppable": True, "is_stackable": True, "data": None, "execute": "", "is_usable": False},

            {"name": "Mobiltelefon", "max_amount": 1, "min_price": 25_000, "max_price": 450_000, "volume": 0, "sellable": True,
             "droppable": True, "is_stackable": True, "data": None, "execute": "", "is_usable": False},
         ]

         for default in defaults:
            if not session.query(Item).where(Item.name == default["name"]).one_or_none():
               session.add(cls(**default))
