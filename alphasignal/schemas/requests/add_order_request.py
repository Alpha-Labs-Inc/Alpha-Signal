from pydantic import BaseModel


class AddOrderRequest(BaseModel):
    mint_address: str
    sell_mode: str
    sell_value: float
    sell_type: str
    balance: float
