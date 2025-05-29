from alphasignal.ai.models.sentiment_response import SentimentResponse
from alphasignal.models.enums import TweetType
from pydantic import BaseModel, Field
from typing import List

from alphasignal.models.token_info import TokenInfo


class ExtractedTweetData(BaseModel):
    tweet_type: TweetType
    tokens: List[TokenInfo] = Field(default_factory=list)
    token_sentiment: SentimentResponse = Field(default_factory=SentimentResponse)
