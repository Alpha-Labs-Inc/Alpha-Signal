from pydantic import BaseModel


class FundPayload(BaseModel):
    funded_wallet_public_key: str
    amt: float
