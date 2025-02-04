from typing import Optional

from pydantic import BaseModel, HttpUrl


class WalletToken(BaseModel):
    token_name: Optional[str]
    token_ticker: Optional[str]
    image: Optional[HttpUrl]
    mint_address: str
    balance: float
    value: float
    usd_balance: Optional[float]
