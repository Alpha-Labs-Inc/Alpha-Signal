from pydantic import BaseModel

from alphasignal.models.enums import AmountType, BuyType, Platform, SellMode, SellType


class Profile(BaseModel):
    id: str
    platform: Platform
    signal: str
    is_active: bool
    buy_type: BuyType
    buy_amount_type: AmountType
    buy_amount: float
    buy_slippage: float
    sell_mode: SellMode
    sell_type: SellType
    sell_value: float
    sell_slippage: float
