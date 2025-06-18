from sqlalchemy import Integer, ForeignKey, select

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column

from sqlalchemy.dialects.postgresql import insert as pg_insert

from pysamp.commands import dispatcher

from python.database.context_managger import transactional_session
from python.server.database import MAIN_SESSION


from .base import Base
from .command import Command 
 
class CommandPermission(Base):
    __tablename__ = 'command_permissions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    command_id: Mapped[int] = mapped_column(ForeignKey("commands.id"), unique=True, nullable=False)
    command: Mapped["Command"] = relationship("Command")
    need_power: Mapped[int] = mapped_column(Integer)


    @classmethod
    def init_defaults(cls) -> None:
        defaults = []

        with transactional_session(MAIN_SESSION) as session:
            for command in [i for i in dispatcher._commands if any(["check_player_role_permission" in str(i) for i in i.requires])]:
                for trigger in command.triggers:
                    cmd_db: Command = session.scalars(select(Command).where(Command.cmd_txt == trigger.replace("/", ""))).one()
                    defaults.append({"command_id": cmd_db.id, "need_power": 2})


            for default in defaults:
                if not session.scalars(select(CommandPermission).where(CommandPermission.command_id == default["command_id"])).one_or_none():
                    session.add(cls(**default))
