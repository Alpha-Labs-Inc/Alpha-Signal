from pydantic import BaseModel


class AutoBuyConfigResponse(BaseModel):
    buy_type: str
    amount_type: str
    amount: float
    slippage: float
