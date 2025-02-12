from enum import Enum


class AmountType(Enum):
    PERCENT = "percent"
    AMOUNT = "amount"


class BuyType(Enum):
    USDC = "USDC"
    SOL = "SOL"


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


class Platform(Enum):
    TWITTER = "twitter"


class TweetSentiment(Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
