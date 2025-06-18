from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base
from .item import Item

class ShopItem(Base):
    __tablename__ = 'shop_items'
    business_id: Mapped[int] = mapped_column(ForeignKey('business.id'), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'), primary_key=True)
    item: Mapped["Item"] = relationship("Item")
    price: Mapped[int] = mapped_column(Integer)
    amount: Mapped[int] = mapped_column(Integer)
    give_amount: Mapped[int] = mapped_column(Integer)