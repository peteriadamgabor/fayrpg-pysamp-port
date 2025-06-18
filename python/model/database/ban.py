from datetime import datetime
from datetime import timezone
from datetime import timedelta

from sqlalchemy import Integer, ForeignKey,  DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base
from .player import Player

from python.database import transactional_session
from python.server.database import MAIN_SESSION
from config import settings

class Ban(Base):
   __tablename__ = 'bans'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
   player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])
   admin_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=True)
   admin: Mapped["Player"] = relationship("Player", foreign_keys=[admin_id])
   ip: Mapped[str] = mapped_column(String)
   banned_at: Mapped[datetime] = mapped_column(DateTime)
   expires_on: Mapped[datetime] = mapped_column(DateTime)
   reason: Mapped[str] = mapped_column(String)


   @classmethod
   def create(cls, player_id: int, admin_id: int | None, ip: str, lenght: int, lenght_type: str, *args) -> None:
      with transactional_session(MAIN_SESSION) as session:
         multiplayer: int = 1


         if lenght_type.lower() in settings.ban_lenght_types.day.names.lower():
            multiplayer = settings.ban_lenght_types.day.multiplayer
         
         elif lenght_type.lower() in settings.ban_lenght_types.hour.names.lower():
            multiplayer = settings.ban_lenght_types.hour.multiplayer
         
         elif lenght_type.lower() in settings.ban_lenght_types.minute.names.lower():
            multiplayer = settings.ban_lenght_types.minute.multiplayer

         utc_now = datetime.now(timezone.utc)
         expire_date = utc_now + timedelta(minutes=(lenght * multiplayer))

         session.add(cls(player_id=player_id, admin_id=admin_id, ip=ip, banned_at=utc_now, expires_on=expire_date, reason=" ".join(args)))
