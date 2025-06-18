from datetime import datetime
from typing import Any

from surrealdb import Surreal, BlockingWsSurrealConnection, BlockingHttpSurrealConnection

from config import settings
from .loggers import exception_logger
from .sqlalchemy import sql_logger

import atexit

from python.utils.enums.log_type import LogTypes

SURREALDB:  BlockingWsSurrealConnection | BlockingHttpSurrealConnection | None = None

class Logger:
    @classmethod
    def write_log(cls, log_type: LogTypes, message: str, toke: str = "", additional_data: dict[str, Any] = None):
        global SURREALDB

        if SURREALDB is None:
            raise Exception("Surreal DB not initialized.")

        log_data = {
            "type": log_type,
            "timestamp": datetime.now(),
            "message": message,
            "player_session_token": toke,
            "additional_data": additional_data
        }

        SURREALDB.create("logs", log_data)

def init_module():
    print(f"Module {__name__} is being initialized.")
    global SURREALDB

    SURREALDB = Surreal(settings.db_surreal.CONNECTION_STRING)
    SURREALDB.signin({"username": settings.db_surreal.USER, "password": settings.secrets.SURREALDB_PASSWORD})
    SURREALDB.use("fay", "server_logs")

    Logger.write_log(LogTypes.SYSTEM, f"Module {__name__} is being initialized.")

def unload_module():
    print(f"Module {__name__} is being unloaded.")
    global SURREALDB

    SURREALDB.close()

atexit.register(unload_module)

init_module()


