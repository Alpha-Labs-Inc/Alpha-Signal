from pydantic import BaseModel


class AutoSellConfigRequest(BaseModel):
    sell_mode: str
    sell_type: str
    sell_value: float
    slippage: float
