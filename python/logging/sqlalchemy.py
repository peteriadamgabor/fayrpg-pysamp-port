import datetime
import logging

logging.basicConfig(filename=f"logs/sqlalchemy/{datetime.datetime.now():%Y-%m-%d}.log", filemode="a+")
sql_logger = logging.getLogger('sqlalchemy.engine')
sql_logger.setLevel(logging.INFO)

