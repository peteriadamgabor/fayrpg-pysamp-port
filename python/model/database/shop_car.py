from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .base import Base
from .vehicle_model import VehicleModel

class ShopCar(Base):
    __tablename__ = 'shop_cars'
    business_id: Mapped[int] = mapped_column(ForeignKey('business.id'), primary_key=True)
    vehicle_model_id: Mapped[int] = mapped_column(ForeignKey('vehicle_models.id'), primary_key=True)
    vehicle_model: Mapped["VehicleModel"] = relationship("VehicleModel")