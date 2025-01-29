from pydantic import BaseModel


class FundResponse(BaseModel):
    funded_wallet_public_key: str
    amt: float
