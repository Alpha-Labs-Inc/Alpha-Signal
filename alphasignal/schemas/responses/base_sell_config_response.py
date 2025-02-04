from pydantic import BaseModel


class BaseSellConfigResponse(BaseModel):
    sell_type: str
    slippage: float
