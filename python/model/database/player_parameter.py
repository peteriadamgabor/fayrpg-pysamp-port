from sqlalchemy import Boolean, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from datetime import datetime


from .base import Base
from .skin import Skin

class PlayerParameter(Base):
   __tablename__ = 'player_parameters'

   player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), primary_key=True)
   fraction_skin_id: Mapped[int] = mapped_column(ForeignKey("skins.id"), nullable=True)
   fraction_skin: Mapped["Skin"] = relationship("Skin")
   payment: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
   today_played: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
   hospital_time: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
   food_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), default=datetime.now)
   job_lock_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), default=datetime.now)
   is_over_limit: Mapped[bool] = mapped_column(Boolean, server_default="0", default=False)
   is_leader: Mapped[bool] = mapped_column(Boolean, server_default="0", default=False)
   is_division_leader: Mapped[bool] = mapped_column(Boolean, server_default="0", default=False)
   fine: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
   deaths: Mapped[int] = mapped_column(Integer, server_default="0", default=0)

