from alphasignal.models.enums import TweetSentiment
from pydantic import BaseModel
from typing import List, Dict


class ExtractedData(BaseModel):
    tickers: List[str]
    solana_addresses: List[str]
    ticker_sentiment: Dict[str, TweetSentiment]
    solana_sentiment: Dict[str, TweetSentiment]
