from pydantic import BaseModel


class QuoteResponse(BaseModel):
    slippage_bps: float
    from_token_amt: float
    to_token_amt: float
    from_token_amt_usd: float
    to_token_amt_usd: float
    conversion_rate: float
    price_impact: float
    price_impact_usd: float
