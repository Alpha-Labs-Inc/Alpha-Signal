from typing import Optional

from pydantic import BaseModel, HttpUrl


class DexScreenerToken(BaseModel):
    token_name: Optional[str]
    token_ticker: Optional[str]
    image: Optional[HttpUrl]
    mint_address: str
    balance: float
    value: float
    usd_balance: Optional[float]
    change_24hr: Optional[float]
    change_6hr: Optional[float]
    change_1hr: Optional[float]
    change_5min: Optional[float]
