from pydantic import BaseModel


class FundRequest(BaseModel):
    funding_private_key: str
    amt: float
