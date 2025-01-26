from datetime import datetime

from pydantic import BaseModel
from alphasignal.models.enums import SellMode


class Coin(BaseModel):
    id: str
    mint_address: str
    last_price_max: float
    sell_mode: SellMode
    sell_value: float
    time_added: datetime
    balance: float
