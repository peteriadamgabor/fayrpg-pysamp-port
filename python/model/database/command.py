from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy.dialects.postgresql import insert as pg_insert

from pysamp.commands import dispatcher

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION

from .base import Base
 
class Command(Base):
    __tablename__ = 'commands'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cmd_txt: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String)


    @classmethod
    def init_defaults(cls) -> None:
        defaults = []

        with transactional_session(MAIN_SESSION) as session:
            for command in dispatcher._commands:
                for trigger in command.triggers:
                    defaults.append({"cmd_txt": trigger.replace("/", ""), "description": ""})

            for default in defaults:
                if not session.scalars(select(Command).where(Command.cmd_txt == default["cmd_txt"])).one_or_none():
                    session.add(cls(**default))