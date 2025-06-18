from sqlalchemy import create_engine

from datetime import datetime
from typing import List, Set

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean, Table, BigInteger, text
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import ColumnProperty, RelationshipProperty
from sqlalchemy import inspect
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm.attributes import instance_state
from sqlalchemy.sql import func

from typing import Optional

from config import settings

__ENGINE = create_engine(settings.db.CONNECTION_STRING, echo=settings.db.ECHO)
