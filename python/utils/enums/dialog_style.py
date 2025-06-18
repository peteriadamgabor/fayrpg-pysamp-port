from enum import Enum


class DialogStyle(int, Enum):
    MSGBOX = 0
    INPUT = 1
    LIST = 2
    PASSWORD = 3
    TABLIST = 4
    TABLIST_HEADERS = 5
