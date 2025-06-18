import json

from sqlalchemy import Integer, String, Boolean, select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION

from .base import Base
from typing import Optional

class Skin(Base):
   __tablename__ = 'skins'
   __allow_unmapped__ = True

   id: Mapped[int]  = mapped_column(Integer, primary_key=True, autoincrement=True)
   gta_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
   description: Mapped[str] = mapped_column(String)
   price: Mapped[int] = mapped_column(Integer)
   sex: Mapped[bool] = mapped_column(Boolean)
   dl_id: Mapped[Optional[int]] = mapped_column(Integer)
   base_id: Mapped[Optional[int]] = mapped_column(Integer)
   dff_path: Mapped[Optional[str]] = mapped_column(String(128))
   txd_path: Mapped[Optional[str]] = mapped_column(String(128))

   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
         with open("scriptfiles/db_defaults/skins.json") as f:
            defaults = json.loads(f.read())

            for default in defaults:
               if not session.scalars(select(Skin).where(Skin.gta_id == default["gta_id"])).one_or_none():
                  session.add(cls(**default))
