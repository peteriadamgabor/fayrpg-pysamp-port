import os.path
import sys

from loguru import logger

__loge_msg_format = "[{time:HH:mm:ss}] {message}"

__system_format = "{time} | {level} | {message}"

__exception_log_path = os.path.join("logs", "exception", "exception_{time:YYYY-MM-DD}.log")
__connection_log_path = os.path.join("logs", "connection", "connection_{time:YYYY-MM-DD}.log")
__money_log_path = os.path.join("logs", "money", "money_{time:YYYY-MM-DD}.log")
__item_log_path = os.path.join("logs", "item", "item_{time:YYYY-MM-DD}.log")
__system_log_path = os.path.join("logs", "system", "system_{time:YYYY-MM-DD}.log")
__console_log_path = os.path.join("logs", "console", "console_{time:YYYY-MM-DD}.log")
__command_log_path = os.path.join("logs", "command", "command_{time:YYYY-MM-DD}.log")
__player_chat_log_path = os.path.join("logs", "playerchat", "playerchat_{time:YYYY-MM-DD}.log")
__anti_cheat_log_path = os.path.join("logs", "anticheat", "anticheat_{time:YYYY-MM-DD}.log")


def __make_filter(name):
    def filter(record):
        return record["extra"].get("name") == name

    return filter

logger.remove()

logger.add(__system_log_path, level="DEBUG", format=__loge_msg_format, rotation="1 days", filter=__make_filter("system"))

logger.add(sys.stdout, level="ERROR", format=__loge_msg_format, backtrace=True, diagnose=True, filter=__make_filter("exception"))

logger.add(__connection_log_path, level="INFO", format=__loge_msg_format, rotation="1 days", filter=__make_filter("connection"))

logger.add(__money_log_path, level="INFO", format=__loge_msg_format, rotation="1 days", filter=__make_filter("money"))

logger.add(__item_log_path, level="INFO", format=__loge_msg_format, rotation="1 days", filter=__make_filter("item"))

logger.add(__command_log_path, level="INFO", rotation="1 days", format=__loge_msg_format, filter=__make_filter("command"))

logger.add(__player_chat_log_path, level="INFO", rotation="1 days", format=__loge_msg_format, filter=__make_filter("player_chat"))

logger.add(__anti_cheat_log_path, level="INFO", rotation="1 days", format=__loge_msg_format, filter=__make_filter("anti_cheat"))

logger.add(sys.stdout, level="DEBUG", format=__system_format, backtrace=True, diagnose=True, filter=__make_filter("debugger"))

logger.add(__console_log_path, level="DEBUG", format=__system_format,
           compression="tar.gz", rotation="1 days",
           backtrace=True, diagnose=True,
           filter=__make_filter("debugger"))

system_logger = logger.bind(name="system")
exception_logger = logger.bind(name="exception")
connection_logger = logger.bind(name="connection")
money_logger = logger.bind(name="money")
item_logger = logger.bind(name="item")
command_logger = logger.bind(name="command")
player_chat_logger = logger.bind(name="player_chat")
anti_cheat_logger = logger.bind(name="anti_cheat")
debugger = logger.bind(name="debugger")
