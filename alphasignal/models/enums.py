from enum import Enum


class SellMode(Enum):
    TIME_BASED = "time_based"
    STOP_LOSS = "stop_loss"


class SellType(Enum):
    USDC = "USDC"
    SOL = "SOL"


class OrderStatus(Enum):
    ACTIVE = 0
    PROCESSING = 1
    COMPLETE = 2
    CANCELED = 3
