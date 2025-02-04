from pydantic import BaseModel


class AutoSellConfigResponse(BaseModel):
    sell_mode: str
    sell_type: str
    sell_value: float
    slippage: float
