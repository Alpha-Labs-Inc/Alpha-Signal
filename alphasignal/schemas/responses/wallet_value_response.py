from typing import List, Optional

from alphasignal.models.wallet_token import WalletToken
from pydantic import BaseModel


class WalletValueResponse(BaseModel):
    wallet_tokens: Optional[List[WalletToken]]
    total_value: float
    percent_change_value_24h: float
