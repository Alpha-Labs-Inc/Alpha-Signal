from enum import Enum


class SellMode(Enum):
    TIME_BASED = "time_based"
    STOP_LOSS = "stop_loss"


class SellType(Enum):
    USDC = "USDC"
    SOL = "SOL"
