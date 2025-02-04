from pydantic import BaseModel


class SwapConfirmationResponse(BaseModel):
    from_token_mint_address: str
    to_token_mint_address: str
    amount: str
