from sqlalchemy import Integer, String, Boolean, BigInteger, select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base
from python.database import transactional_session
from python.server.database import MAIN_SESSION
from python.utils.helper.python import load_json_file


class VehicleColor(Base):
   __tablename__ = 'vehicle_colors'
   __allow_unmapped__ = True

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   gta_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
   rgb: Mapped[str] = mapped_column(String)
   hex: Mapped[str] = mapped_column(String)
   name: Mapped[str] = mapped_column(String)
   easy_name: Mapped[str] = mapped_column(String)
   can_paint: Mapped[bool] = mapped_column(Boolean, default=True, server_default="True")
   price: Mapped[int] = mapped_column(BigInteger)

   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
         defaults = load_json_file("scriptfiles/db_defaults/vehicle_colors.json")

         for default in defaults:
            if not session.scalars(select(VehicleColor).where(VehicleColor.gta_id == default["gta_id"])).one_or_none():
               session.add(cls(**default))
