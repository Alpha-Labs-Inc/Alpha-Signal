from pydantic import BaseModel


class SwapConfirmation(BaseModel):
    from_token_mint_address: float
    to_token_mint_address: float
    transaction_simulator: str
