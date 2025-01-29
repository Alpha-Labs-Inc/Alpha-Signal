from pydantic import BaseModel


class SwapQuoteRequest(BaseModel):
    from_token_mint_address: str
    to_token_mint_address: str
    amt: float
