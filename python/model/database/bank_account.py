from sqlalchemy import Integer, String, Float, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from .base import Base
from .player import Player
from .business import Business
from .fraction import Fraction

class BankAccount(Base):
    __tablename__ = 'bank_accounts'
    __allow_unmapped__ = True

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    balance: Mapped[float] = mapped_column(BigInteger)
    owner_id: Mapped[int] = mapped_column(ForeignKey("players.id"))
    owner: Mapped["Player"] = relationship("Player")
    business_id: Mapped[int] = mapped_column(ForeignKey("business.id"))
    business: Mapped["Business"] = relationship("Business")
    fraction_id: Mapped[int] = mapped_column(ForeignKey("fractions.id"))
    fraction: Mapped["Fraction"] = relationship("Fraction")
    is_default: Mapped[bool] = mapped_column(Boolean)
