from typing import List
from pydantic import BaseModel, Field

from alphasignal.models.enums import TweetSentiment
from alphasignal.models.token_info import TokenInfo


class TokenSentiment(BaseModel):
    token: TokenInfo = Field(
        description="The mint or contract address of a token.  Will only have 1 or the other, most likely"
    )  # can be the mint address or contract address
    sentiment: TweetSentiment = Field(
        description="The sentiment of the tweet toward the specific token."
    )

    class Config:
        use_enum_values = True


class SentimentResponse(BaseModel):
    response: List[TokenSentiment] = Field(
        description="A list of token sentiments for a given tweet."
    )

    class Config:
        use_enum_values = True
