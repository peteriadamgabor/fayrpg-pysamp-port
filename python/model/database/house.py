from datetime import datetime

from sqlalchemy import Integer, Float, DateTime, ForeignKey, Boolean, BigInteger, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from python.database import transactional_session
from python.server.database import MAIN_SESSION
from python.utils.helper.python import load_json_file

from .base import Base
from .player import Player
from .house_type import HouseType


class House(Base):
   __tablename__ = 'houses'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   house_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
   entry_x: Mapped[float] = mapped_column(Float)
   entry_y: Mapped[float] = mapped_column(Float)
   entry_z: Mapped[float] = mapped_column(Float)
   angle: Mapped[float] = mapped_column(Float)
   locked: Mapped[bool] = mapped_column(Boolean, server_default="0", default=False)
   price: Mapped[int] = mapped_column(BigInteger)
   type: Mapped[int] = mapped_column(Integer)
   rent_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
   is_spawn: Mapped[bool] = mapped_column(Boolean, server_default="0", default=False)
   owner_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=True)
   owner: Mapped[Player] = relationship("Player")
   house_type_id: Mapped[int] = mapped_column(ForeignKey("house_types.id"))
   house_type: Mapped[HouseType] = relationship("HouseType")
   is_robbed: Mapped[bool] = mapped_column(Boolean, server_default="0", default=False)
   lockpick_time: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
   alarm_lvl: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
   door_lvl: Mapped[int] = mapped_column(Integer, server_default="0", default=0)


   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
         defaults = load_json_file("scriptfiles/db_defaults/houses.json")

         for default in defaults:
            if not session.scalars(select(House).where(House.house_number == default["house_number"])).one_or_none():
               session.add(cls(**default))
