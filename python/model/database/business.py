from sqlalchemy import Float, ForeignKey, Boolean, BigInteger, Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from python.database import transactional_session
from python.server.database import MAIN_SESSION
from python.utils.helper.python import load_json_file

from .interior import Interior
from .player import Player
from .business_type import BusinessType
from .skin import Skin
from .shop_item import ShopItem
from .shop_car import ShopCar
from .base import Base


class Business(Base):
    __tablename__ = 'business'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    in_game_id: Mapped[int] = mapped_column(Integer)
    business_type_id: Mapped[int] = mapped_column(ForeignKey("business_types.id"))
    business_type: Mapped["BusinessType"] = relationship("BusinessType")
    interior_id: Mapped[int] = mapped_column(ForeignKey("interiors.id"))
    interior: Mapped["Interior"] = relationship("Interior")
    owner_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    owner: Mapped["Player"] = relationship("Player")
    price: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String)
    x: Mapped[float] = mapped_column(Float)
    y: Mapped[float] = mapped_column(Float)
    z: Mapped[float] = mapped_column(Float)
    a: Mapped[float] = mapped_column(Float)
    load_x: Mapped[float] = mapped_column(Float)
    load_y: Mapped[float] = mapped_column(Float)
    load_z: Mapped[float] = mapped_column(Float)
    load_a: Mapped[float] = mapped_column(Float)
    locked: Mapped[bool] = mapped_column(Boolean, server_default="0", default=False)
    company_chain: Mapped[int] = mapped_column(Integer)
    is_illegal: Mapped[bool] = mapped_column(Boolean, server_default="0", default=False)
    skins: Mapped[list["Skin"]] = relationship("Skin", secondary="shop_skins")
    items: Mapped[list["ShopItem"]] = relationship("ShopItem")
    cars: Mapped[list["ShopCar"]] = relationship("ShopCar")
    business_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)

    @classmethod
    def init_defaults(cls) -> None:
        with transactional_session(MAIN_SESSION) as session:
            defaults = load_json_file("scriptfiles/db_defaults/business.json")

            for default in defaults:
                if not session.scalars(select(Business).where(Business.business_number == default["business_number"])).one_or_none():
                    session.add(cls(**default))
