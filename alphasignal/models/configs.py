from pydantic import BaseModel

from alphasignal.models.enums import AmountType, BuyType, SellMode, SellType


class AutoBuyConfig(BaseModel):
    buy_type: BuyType
    amount_type: AmountType
    amount: float
    slippage: float


class AutoSellConfig(BaseModel):
    sell_mode: SellMode
    sell_type: SellType
    sell_value: float
    slippage: float


class BaseSellConfig(BaseModel):
    sell_type: SellType
    slippage: float
