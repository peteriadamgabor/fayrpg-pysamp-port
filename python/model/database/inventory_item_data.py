from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base
from .vehicle import Vehicle


class InventoryItemData(Base):
    __tablename__ = 'inventory_item_data'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    vehicle: Mapped[Vehicle] = relationship("Vehicle")
