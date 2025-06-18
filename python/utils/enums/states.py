from enum import Enum


class State(int, Enum):
    NONE = 0
    ON_FOOT = 1
    DRIVER = 2
    PASSENGER = 3
    EXIT_VEHICLE = 4
    ENTER_VEHICLE_DRIVER = 5
    ENTER_VEHICLE_PASSENGER = 6
    WASTED = 7
    SPAWNED = 8
    SPECTATING = 9
