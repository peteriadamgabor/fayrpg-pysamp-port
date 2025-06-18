import json

from sqlalchemy import Integer, String, Float, select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base
from python.database import transactional_session
from python.server.database import MAIN_SESSION
from python.utils.helper.python import load_json_file


class HouseType(Base):
   __tablename__ = 'house_types'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
   enter_x: Mapped[float] = mapped_column(Float)
   enter_y: Mapped[float] = mapped_column(Float)
   enter_z: Mapped[float] = mapped_column(Float)
   angle: Mapped[float] = mapped_column(Float)
   interior: Mapped[int] = mapped_column(Integer)
   description: Mapped[str] = mapped_column(String)
   price: Mapped[int] = mapped_column(Integer)
   max_alarm_lvl: Mapped[int] = mapped_column(Integer)
   max_door_lvl: Mapped[int] = mapped_column(Integer)


   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
         defaults = load_json_file("scriptfiles/db_defaults/house_types.json")

         for default in defaults:
            if not session.scalars(select(HouseType).where(HouseType.code == default["code"])).one_or_none():
               session.add(cls(**default))
