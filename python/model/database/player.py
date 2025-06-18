from sqlalchemy import Integer, String, DateTime, Date, ForeignKey, Float, BigInteger, text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column

from datetime import date, datetime

from .base import Base
from .skin import Skin
from .role import Role
from .player_parameter import PlayerParameter
from .fraction import Fraction
from .division import Division
from .rank import Rank
from .inventory_item import InventoryItem

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION

class Player(Base):
    __tablename__ = 'players'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    account: Mapped["Account"] = relationship("Account", secondary="account_players")
    in_game_id: Mapped[int] = mapped_column(Integer, nullable=True)
    name: Mapped[str] = mapped_column(String(26), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(512))
    money: Mapped[int] = mapped_column(BigInteger, server_default="275000", default=275000)
    skin_id: Mapped[int] = mapped_column(ForeignKey("skins.id"), server_default="27", default=27)
    skin: Mapped["Skin"] = relationship("Skin")
    sex: Mapped[int] = mapped_column(Integer)
    health: Mapped[float] = mapped_column(Float, server_default="100.0", default=100.0)
    played_time: Mapped[int] = mapped_column("playedtime", Integer, server_default="0", default=0)
    birthdate: Mapped[date] = mapped_column(Date)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), nullable=True)
    role: Mapped["Role"] = relationship("Role")
    parameter: Mapped["PlayerParameter"] = relationship("PlayerParameter")
    fraction_id: Mapped[int] = mapped_column(ForeignKey("fractions.id"), nullable=True)
    fraction: Mapped["Fraction"] = relationship("Fraction")
    division_id: Mapped[int] = mapped_column(ForeignKey("divisions.id"), nullable=True)
    division: Mapped["Division"] = relationship("Division")
    rank_id: Mapped[int] = mapped_column(ForeignKey("ranks.id"), nullable=True)
    rank: Mapped["Rank"] = relationship("Rank")
    is_activated: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
    job_id: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
    registration_time: Mapped[datetime] = mapped_column(DateTime, server_default=text('NOW()'), default=datetime.now)


    @classmethod
    def init_defaults(cls) -> None:
        with transactional_session(MAIN_SESSION) as session:
            defaults = [
                {"name": "Pavlo_Iljics_Zivon", "password": "Szifon", "sex": 0, "birth": "1998-03-26"},
                {"name": "Brian_Murray", "password": "Bnece", "sex": 0, "birth": "1997-02-11"},
            ]

            for default in defaults:
                if not session.query(Player).where(Player.name == default["name"]).one_or_none():
                    session.execute(text("SELECT insert_player(:name, :password, :sex, :birth);"), default)
