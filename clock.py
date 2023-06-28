from enum import Enum


class GlobalTime(Enum):
    SLOW = 1
    FAST = 5
    SUPER_FAST = 10


GLOBAL_TIME = GlobalTime.SLOW
