from sqlalchemy import Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION

from .base import Base
from .item import Item
from .inventory_item_data import InventoryItemData

class InventoryItem(Base):
   __tablename__ = 'inventory_items'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   item_id: Mapped[int] = mapped_column(ForeignKey("items.id"))
   item: Mapped[Item] = relationship("Item")
   inventory_item_data_id: Mapped[int] = mapped_column(ForeignKey("inventory_item_data.id"))
   inventory_item_data: Mapped["InventoryItemData"] = relationship("InventoryItemData")
   player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
   player: Mapped["Player"] = relationship("Player")
   amount: Mapped[int] = mapped_column(Integer)
   worn: Mapped[bool] = mapped_column(Boolean)
   dead: Mapped[bool] = mapped_column(Boolean)
   
   @classmethod
   def create(cls, player_id: int, item_id: int, amount: int, *args) -> None:
      with transactional_session(MAIN_SESSION) as session:
         session.add(cls(item_id=item_id, player_id=player_id, amount=amount, worn=False, dead=False))

