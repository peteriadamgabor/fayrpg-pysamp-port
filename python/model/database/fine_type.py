from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import insert as pg_insert

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION

from .base import Base

class FineType(Base):
   __tablename__ = 'fine_types'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
   name: Mapped[str] = mapped_column(String(256), nullable=False)
   description: Mapped[str] = mapped_column(String(256), server_default="", default="")

   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
         defaults = [ {"code": "HF", "name": "Kórházi számla", "description": ""},
                      {"code": "PDF", "name": "Rendőrségi bírság", "description": ""},
                      {"code": "SYSF", "name": "Rendszer tartozás", "description": ""},
                      {"code": "AF", "name": "Admin bírság", "description": ""}
                    ]

         for default in defaults:
             if not session.scalars(select(FineType).where(FineType.code == default["code"])).one_or_none():
                 session.add(cls(**default))
