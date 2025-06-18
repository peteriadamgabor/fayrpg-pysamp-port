from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.orm import mapped_column

from .base import Base

from datetime import datetime

class Account(Base):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(256), nullable=False)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(512))
    otp_secret: Mapped[str] = mapped_column(String(64))
    otp_enabled: Mapped[int] = mapped_column(Integer, server_default="0", default=0)
    otp_skip_until: Mapped[datetime] = mapped_column(DateTime)
    players: Mapped[list["Player"]] = relationship("Player", secondary="account_players")

