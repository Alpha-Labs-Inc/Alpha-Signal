from alphasignal.models.enums import TweetSentiment, TweetType
from pydantic import BaseModel
from typing import List, Tuple

from alphasignal.models.token_info import TokenInfo


class ExtractedTweetData(BaseModel):
    tweet_type: TweetType
    tokens: List[TokenInfo] = []
    token_sentiment: List[Tuple[TokenInfo, TweetSentiment]] = []
