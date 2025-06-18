from sqlalchemy import Integer, String, Boolean, BigInteger, select
from sqlalchemy.orm import  relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base
from .fuel_type import FuelType
from .tabels import vehicle_model_fuels
from ...database import transactional_session
from ...server.database import MAIN_SESSION
from ...utils.helper.python import load_json_file


class VehicleModel(Base):
   __tablename__ = 'vehicle_models'
   __allow_unmapped__ = True

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
   real_name: Mapped[str] = mapped_column(String)
   seats: Mapped[int] = mapped_column(Integer)
   price: Mapped[int] = mapped_column(BigInteger)
   trunk_capacity: Mapped[int] = mapped_column(Integer)
   color_number: Mapped[int] = mapped_column(Integer)
   tank_capacity: Mapped[int] = mapped_column(Integer)
   consumption: Mapped[int] = mapped_column(Integer)
   max_speed: Mapped[int] = mapped_column(Integer)
   hood: Mapped[bool] = mapped_column(Boolean)
   airbag: Mapped[bool] = mapped_column(Boolean)
   allowed_fuel_types: Mapped[list[FuelType]] = relationship('FuelType', secondary="vehicle_model_fuels")

   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
         defaults = load_json_file("scriptfiles/db_defaults/vehicle_models.json")

         for default in defaults:
            if not session.scalars(select(VehicleModel).where(VehicleModel.name == default["name"])).one_or_none():
               session.add(cls(**default))
