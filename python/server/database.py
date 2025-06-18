from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings


__ENGINE = create_engine(settings.db.CONNECTION_STRING, echo=settings.db.ECHO)

LOADER_SESSION = sessionmaker(__ENGINE)
MAIN_SESSION = sessionmaker(__ENGINE)
PLAYER_SESSION = sessionmaker(__ENGINE)
HOUSE_SESSION = sessionmaker(__ENGINE)
ITEM_SESSION = sessionmaker(__ENGINE)
UTIL_SESSION = sessionmaker(__ENGINE)
VEHICLE_SESSION = sessionmaker(__ENGINE)
BUSINESS_SESSION = sessionmaker(__ENGINE)
