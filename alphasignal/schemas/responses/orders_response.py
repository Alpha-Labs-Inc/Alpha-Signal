from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class OrderResponse(BaseModel):
    id: str
    mint_address: str
    last_price_max: float
    sell_mode: str
    sell_value: float
    sell_type: str
    time_added: datetime
    balance: float
    status: int
    profit: Optional[str]
    slippage: float


class OrdersResponse(BaseModel):
    orders: List[OrderResponse]
