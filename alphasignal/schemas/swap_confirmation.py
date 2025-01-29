from pydantic import BaseModel


class SwapConfirmation(BaseModel):
    from_token_mint_address: str
    to_token_mint_address: str
    transaction_str: str
