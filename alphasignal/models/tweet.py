from pydantic import BaseModel
from datetime import datetime


class Tweet(BaseModel):
    id: str
    full_text: str
    is_retweet: bool
    is_reply: bool
    tickers: list[str] = []
    contract_addresses: list[str] = []
    created_at: datetime
