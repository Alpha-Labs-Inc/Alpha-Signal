from typing import Optional

from pydantic import BaseModel


class WalletToken(BaseModel):
    mint_address: str
    balance: float
    value: float
    token_name: Optional[str] = None  # Default to None if name is unavailable