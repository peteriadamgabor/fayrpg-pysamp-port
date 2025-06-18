from enum import Enum


class JobsTypeEnum(int, Enum):
    NONE = 0  # N/A
    SWEEPER = 1
    BOATDELIVERY = 2
    FISHERMAN = 3