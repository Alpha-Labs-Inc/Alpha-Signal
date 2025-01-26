from typing import Any
from pydantic import BaseModel
from solders.keypair import Keypair
from solders.pubkey import Pubkey


class Wallet(BaseModel):
    public_key: Any
    wallet_keypair: Any
