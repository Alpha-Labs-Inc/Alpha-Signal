from pydantic import BaseModel


class AutoBuyConfigRequest(BaseModel):
    buy_type: str
    amount_type: str
    amount: float
    slippage: float
