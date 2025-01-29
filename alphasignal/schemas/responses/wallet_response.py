from pydantic import BaseModel


class WalletResponse(BaseModel):
    public_key: str
    wallet_keypair: str
