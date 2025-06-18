import random
import string
from sqlalchemy import Integer, String, Float, ForeignKey, Boolean, BigInteger, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base

from .vehicle_model import VehicleModel
from .fuel_type import FuelType
from .fraction import Fraction

from python.database import transactional_session
from python.server.database import MAIN_SESSION

class Vehicle(Base):
   __tablename__ = 'vehicles'
   __allow_unmapped__ = True

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   in_game_id: Mapped[int] = mapped_column(Integer)
   vehicle_model_id: Mapped[int] = mapped_column("model_id", Integer, ForeignKey("vehicle_models.id"))
   model: Mapped[VehicleModel] = relationship("VehicleModel")
   x: Mapped[float] = mapped_column(Float)
   y: Mapped[float] = mapped_column(Float)
   z: Mapped[float] = mapped_column(Float)
   angle: Mapped[float] = mapped_column(Float)
   color_1: Mapped[int] = mapped_column(Integer, server_default="1", default=1)
   color_2: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
   fuel_type_id: Mapped[int] = mapped_column(ForeignKey("fuel_types.id"))
   fuel_type: Mapped[FuelType] = relationship("FuelType", foreign_keys=[fuel_type_id])
   fill_type_id: Mapped[int] = mapped_column(ForeignKey("fuel_types.id"))
   fill_type: Mapped[FuelType] = relationship("FuelType", foreign_keys=[fill_type_id])
   fuel_level: Mapped[float] = mapped_column(Float)
   locked: Mapped[bool] = mapped_column(Boolean, server_default="0", default=False)
   health: Mapped[float] = mapped_column(Float, server_default="1000.0", default=1000.0)
   plate: Mapped[str] = mapped_column(String)
   panels_damage: Mapped[int] = mapped_column(BigInteger, server_default="0", default=0)
   doors_damage: Mapped[int] = mapped_column(BigInteger, server_default="0", default=0)
   lights_damage: Mapped[int] = mapped_column(BigInteger, server_default="0", default=0)
   tires_damage: Mapped[int] = mapped_column(BigInteger, server_default="0", default=0)
   distance: Mapped[int] = mapped_column(BigInteger, server_default="0", default=0)
   job_id: Mapped[int] = mapped_column(Integer)
   fraction_id: Mapped[int] = mapped_column(ForeignKey("fractions.id"), nullable=True)
   fraction: Mapped["Fraction"] = relationship("Fraction")
   is_rentabel: Mapped[bool] = mapped_column(Boolean, server_default="0", default=False)
   rent_price: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
   rent_time: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
   owner_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
   owner: Mapped["Player"] = relationship("Player", foreign_keys=[owner_id])

   @classmethod
   def create(cls, vehicle_model_id: int, x: float, y: float, z: float, angle: float, color_1: int, color_2:int | None, fuel_type_id: int, owner_id: int, fraction_id: int | None, *args) -> str:

      from . import Player

      with transactional_session(MAIN_SESSION) as session:
         player: Player | None = session.scalars(select(Player).where(Player.id == owner_id)).one_or_none()
         fraction: Fraction | None = session.scalars(select(Fraction).where(Fraction.id == fraction_id)).one_or_none()
         fuel_type: FuelType | None = session.scalars(select(FuelType).where(FuelType.id == fuel_type_id)).one()
         vehicle_model: VehicleModel | None = session.scalars(select(VehicleModel).where(VehicleModel.id == vehicle_model_id)).one()

         letters = ''.join(random.choices(string.ascii_uppercase, k=3))
         numbers = ''.join(random.choices(string.digits, k=3))
         plate = f"{letters}-{numbers}"

         new_vehicle: Vehicle = Vehicle(model=vehicle_model, x=x, y=y, z=z, angle=angle, fuel_type=fuel_type, fill_type=fuel_type, fuel_level=vehicle_model.tank_capacity, owner=player, fraction=fraction, color_1=color_1, color_2=color_2, plate=plate)

         session.add(new_vehicle)

         return plate