from pydantic import BaseModel


class ProfileUpdateRequest(BaseModel):
    buy_type: str
    buy_amount_type: str
    buy_amount: float
    buy_slippage: float
    sell_mode: str
    sell_type: str
    sell_value: float
    sell_slippage: float
