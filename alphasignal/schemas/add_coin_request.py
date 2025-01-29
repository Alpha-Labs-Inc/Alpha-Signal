from pydantic import BaseModel


class AddCoinRequest(BaseModel):
    mint_address: str
    sell_mode: str
    sell_value: str
    sell_type: str
    balance: float
