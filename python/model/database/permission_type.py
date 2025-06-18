from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from .base import Base

from sqlalchemy.dialects.postgresql import insert as pg_insert

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION

class PermissionType(Base):
   __tablename__ = 'permission_types'

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   name: Mapped[str] = mapped_column(String)
   code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
   description: Mapped[str] = mapped_column(String)


   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
         defaults = [
                     {"name": "System edit",       "code": "server_edit",  "description": "" },
                     {"name": "Edit players",      "code": "player_edit",  "description": "" },
                     {"name": "Moderate player",   "code": "player_mod",   "description": "" },
                     {"name": "Edit vehciles",     "code": "vehicle_edit", "description": "" },
                     {"name": "Moderate vehicles", "code": "vehicle_mod",  "description": "" },
                     {"name": "Admin power",       "code": "admin_power",  "description": "" },
                    ]

         for default in defaults:
            session.execute(pg_insert(PermissionType).values(**default).on_conflict_do_nothing(index_elements=["code"]))
