from sqlalchemy import Boolean, Integer, String, select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION

from .base import Base
from .role_permission import RolePermission

class ReportCategory(Base):
   __tablename__ = 'report_categories'
   __allow_unmapped__ = True

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
   name: Mapped[str] = mapped_column(String, nullable=False)
   color: Mapped[str] = mapped_column(String, nullable=False)
   is_deletabel: Mapped[bool] = mapped_column(Boolean, server_default="1", default=True)
   is_visible: Mapped[bool] = mapped_column(Boolean, server_default="1", default=True)
   order: Mapped[int] = mapped_column(Integer)

   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
         defaults = [
                     {"code": "AFK",          "name": "AFK",                                               "order": -1, "color": "FFFFFF", "is_visible": False},
                     {"code": "MINDEN",       "name": "Minden",                                            "order": 0,  "color": "FFFFFF", "is_visible": False},
                     {"code": "NonRP/Cheat",  "name": "Szabályszegők / Csalók",                            "order": 1,  "color": "4682B4" },
                     {"code": "Game",         "name": "Játékmenettel kapcsolatos kérdése",                 "order": 2,  "color": "5AC750" },
                     {"code": "Car/Item/Bug", "name": "Jármű problémák / Elveszett cuccok / Hibajelentés", "order": 3,  "color": "FFC6AA" },
                     {"code": "RP-teszt/Web", "name": "Szabályzatból kérdeztek / Gondok a honlapon",       "order": 4,  "color": "D2691E" },
                    ]

         for default in defaults:
             if not session.scalars(select(ReportCategory).where(ReportCategory.code == default["code"])).one_or_none():
                 session.add(cls(**default))

