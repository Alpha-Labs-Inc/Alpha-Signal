from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from alphasignal.models.enums import OrderStatus, SellMode, SellType


class Order(BaseModel):
    id: str
    mint_address: str
    last_price_max: float
    sell_mode: SellMode
    sell_value: float
    sell_type: SellType
    time_added: datetime
    balance: float
    status: OrderStatus
    profit: Optional[str]
    slippage: float
