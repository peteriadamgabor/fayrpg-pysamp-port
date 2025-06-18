from datetime import datetime

from sqlalchemy import Integer, ForeignKey,  DateTime, String, BigInteger, Boolean, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base
from .player import Player
from .fine_type import FineType

from python.database import transactional_session
from python.server.database import MAIN_SESSION

class PlayerFine(Base):
   __tablename__ = 'player_fines'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   
   player_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
   player: Mapped["Player"] = relationship("Player", foreign_keys=[player_id])

   issuer_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
   issuer: Mapped["Player"] = relationship("Player", foreign_keys=[issuer_id])
   
   fine_type_id: Mapped[int] = mapped_column(ForeignKey("fine_types.id"))
   fine_type: Mapped["FineType"] = relationship("FineType", foreign_keys=[fine_type_id])

   issued: Mapped[datetime] = mapped_column(DateTime)
   amount: Mapped[int] = mapped_column(BigInteger)
   payed_amount: Mapped[int] = mapped_column(BigInteger, server_default="0", default=0)
   reason: Mapped[str] = mapped_column(String(256))

   is_payed: Mapped[bool] = mapped_column(Boolean, server_default="0", default=False)

   @classmethod
   def create(cls, player_id: int, issuer_id: int | None, fine_type_code: str, amount: int, reason: str, *args) -> None:
      with transactional_session(MAIN_SESSION) as session:
         fine_type: FineType = session.scalars(select(FineType).where(FineType.code == fine_type_code)).one()

         datetime_now = datetime.now()
         session.add(cls(player_id=player_id, issuer_id=issuer_id, fine_type_id=fine_type.id, issued=datetime_now, amount=amount, reason=reason))
