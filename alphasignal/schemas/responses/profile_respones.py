from pydantic import BaseModel


class ProfileResponse(BaseModel):
    id: str
    platform: str
    username: str
    is_active: bool
    buy_type: str
    buy_amount_type: str
    buy_amount: float
    buy_slippage: float
    sell_mode: str
    sell_type: str
    sell_value: float
    sell_slippage: float
