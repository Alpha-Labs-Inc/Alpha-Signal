from alphasignal.ai.models.sentiment_response import SentimentResponse
from alphasignal.models.enums import TweetType
from pydantic import BaseModel
from typing import List

from alphasignal.models.token_info import TokenInfo


class ExtractedTweetData(BaseModel):
    tweet_type: TweetType
    tokens: List[TokenInfo] = []
    token_sentiment: SentimentResponse = []
