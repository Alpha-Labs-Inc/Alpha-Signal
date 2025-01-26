from typing import Any
from pydantic import BaseModel


class TokenValue(BaseModel):
    token_mint_address: str
    price: float
