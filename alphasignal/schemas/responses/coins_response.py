from datetime import datetime
from typing import List
from pydantic import BaseModel


class CoinResponse(BaseModel):
    id: str
    mint_address: str
    last_price_max: float
    sell_mode: str
    sell_value: float
    sell_type: str
    time_added: datetime
    balance: float


class CoinsResponse(BaseModel):
    coins: List[CoinResponse]
