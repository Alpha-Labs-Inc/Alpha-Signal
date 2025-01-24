from datetime import datetime

from pydantic import BaseModel
from alphasignal.modles.enums import SellMode


class Coin(BaseModel):
    id: str
    mint_address: str
    last_price_max: float
    sell_mode: SellMode
    sell_value: float
    time_purchased: datetime
    buy_in_value: float