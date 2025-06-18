from sqlalchemy import Integer, select
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION

from .base import Base

class BusinessType(Base):
    __tablename__ = 'business_types'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False,)

    @classmethod
    def init_defaults(cls) -> None:
      with transactional_session(MAIN_SESSION) as session:
        defaults = [
                        {"code": "BANK",                "name": "Bank" },
                        {"code": "CARDEALERSHIP",       "name": "Autó szalon" },
                        {"code": "RETAILCARDEALERSHIP", "name": "Használtautó kereskedés" },
                        {"code": "STORE",               "name": "Bolt" },
                        {"code": "RESTAURANT",          "name": "Étterem" },
                        {"code": "FASTFOODRESTAURANT",  "name": "Gyorsétterem" },
                        {"code": "CLOTHSHOP",           "name": "Ruhabolt" },
                    ]

        for default in defaults:
            if not session.scalars(select(BusinessType).where(BusinessType.code == default["code"])).one_or_none():
                session.add(cls(**default))