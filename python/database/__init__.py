from datetime import datetime

from config import settings
from .context_managger import transactional_session

from surrealdb import Surreal, BlockingWsSurrealConnection, BlockingHttpSurrealConnection

import atexit


class SessionLogger:
    SURREALDB: BlockingWsSurrealConnection | BlockingHttpSurrealConnection = Surreal(settings.db_surreal.CONNECTION_STRING)
    SURREALDB.signin({"username": settings.db_surreal.USER, "password": settings.secrets.SURREALDB_PASSWORD})
    SURREALDB.use("fay", "player_sessions")

    @classmethod
    def add_session(cls, player_name: str, token: str ):
        if SURREALDB is None:
            raise Exception("Surreal DB not initialized.")

        session = {
            "valid_from": datetime.now(),
            "player_name": player_name,
            "token": token,
            "valid_to": None
        }

        SURREALDB.create("player_session", session)


    @classmethod
    def close_session(cls, player_name: str, token: str):
        if SURREALDB is None:
            raise Exception("Surreal DB not initialized.")

        session = {
            "valid_from": datetime.now().isoformat(),
            "player_name": player_name,
            "token": token,
            "valid_to": None
        }

        SURREALDB.create("player_session", session)

def init_module():
    print(f"Module {__name__} is being initialized.")


def unload_module():
    print(f"Module {__name__} is being unloaded.")
    global SURREALDB

    SURREALDB.close()

atexit.register(unload_module)

init_module()