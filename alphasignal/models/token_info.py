from pydantic import BaseModel, HttpUrl, model_validator
from typing import Optional


class TokenInfo(BaseModel):
    mint_address: Optional[str] = None
    ticker: Optional[str] = None
    name: Optional[str] = None
    image: Optional[HttpUrl] = None

    @model_validator(mode="before")
    def check_mint_address_or_ticker(cls, values):
        mint_address = values.get("mint_address")
        ticker = values.get("ticker")
        if not mint_address and not ticker:
            raise ValueError("Either mint_address or ticker must be provided")
        return values
