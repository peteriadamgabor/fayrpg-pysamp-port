from enum import Enum


class ZoneType(int, Enum):
    TELEPORT = 0
    DUTY_LOCATION = 1
    BUSINESS_EXIT = 2

    TELCOTOWER = 100

    RACE_SECTOR = 1_000
    RACE_TIMING_LINE = 1_001
    RACE_BOX_IN_LINE = 1_002
    RACE_BOX_OUT_LINE = 1_003
