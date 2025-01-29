from pydantic import BaseModel


class PayloadWallet(BaseModel):
    public_key: str
    wallet_keypair: str
