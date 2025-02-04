from pydantic import BaseModel, HttpUrl
from typing import Optional


class TokenInfo(BaseModel):
    mint_address: str
    name: str
    ticker: str
    image: Optional[HttpUrl]
