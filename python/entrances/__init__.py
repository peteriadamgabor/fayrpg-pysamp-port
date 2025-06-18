import atexit

from sqlalchemy import select
from python.database.context_managger import transactional_session
from python.server.database import UTIL_SESSION
from python.model.server import Entrance
from python.model.database import Teleport as TeleportDB

def init_module():
    print(f"Module {__name__} is being initialized.")

    load()


def load():
    with transactional_session(UTIL_SESSION) as session:
        teleports: list[TeleportDB] = list(session.scalars(select(TeleportDB)).all())

        for teleport in teleports:
            Entrance(teleport.from_x, teleport.from_y, teleport.from_z, teleport.from_angel,
                     teleport.from_vw, teleport.from_interior,
                     teleport.to_x, teleport.to_y, teleport.to_z, teleport.to_angel,
                     teleport.to_interior, teleport.to_vw, 
                     teleport.description, teleport.radius)


def unload_module():
    print(f"Module {__name__} is being unloaded.")
    

atexit.register(unload_module)

init_module()

from . import commands
