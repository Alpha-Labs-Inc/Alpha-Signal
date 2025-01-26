from typing import List, Optional

from alphasignal.models.wallet_token import WalletToken
from pydantic import BaseModel


class WalletValue(BaseModel):
    wallet_tokens: Optional[List[WalletToken]]
    total_value: float
