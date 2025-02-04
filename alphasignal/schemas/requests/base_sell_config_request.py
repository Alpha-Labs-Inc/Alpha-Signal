from pydantic import BaseModel


class BaseSellConfigRequest(BaseModel):
    sell_type: str
    slippage: float
