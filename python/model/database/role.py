from sqlalchemy import Boolean, Integer, String, select
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION

from .base import Base
from .role_permission import RolePermission

class Role(Base):
   __tablename__ = 'roles'
   __allow_unmapped__ = True

   id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
   name: Mapped[str] = mapped_column(String)
   code: Mapped[str] = mapped_column(String, unique=True, nullable=False, server_default="N/A", default="N/A")
   is_visible: Mapped[bool] = mapped_column(Boolean, server_default="1", default=True)
   permissions: Mapped[list[RolePermission]] = relationship("RolePermission", primaryjoin="Role.id == RolePermission.role_id")
   power: Mapped[int] = mapped_column(Integer)

   @classmethod
   def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
         defaults = [
                     {"code": "AS",  "name": "Adminsegéd", "power": 1, "is_visible": False },
                     {"code": "VIP", "name": "VIP",        "power": 2, "is_visible": True  },
                     {"code": "MOD", "name": "Moderátor",  "power": 3, "is_visible": True  },
                     {"code": "1A",  "name": "1 Admin",    "power": 4, "is_visible": True  },
                     {"code": "2A",  "name": "2 Admin",    "power": 5, "is_visible": True  },
                     {"code": "3A",  "name": "3 Admin",    "power": 6, "is_visible": True  },
                     {"code": "4A",  "name": "4 Admin",    "power": 7, "is_visible": True  },
                     {"code": "DEV", "name": "Fejlesztő",  "power": 8, "is_visible": True  }
                    ]

         for default in defaults:
             if not session.scalars(select(Role).where(Role.code == default["code"])).one_or_none():
                 session.add(cls(**default))
