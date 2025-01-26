from typing import Any
from pydantic import BaseModel
from solders.keypair import Keypair
from solders.pubkey import Pubkey


class MintToken(BaseModel):
    token_mint_address: str
    token_mint_pubkey: Any
