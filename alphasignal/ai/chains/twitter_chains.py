from pydantic import ValidationError
from alphasignal.ai.llm import LLM
from alphasignal.ai.models.sentiment_response import SentimentResponse
from alphasignal.models.token_info import TokenInfo
from typing import List
from alphasignal.ai.prompts.twitter_prompts import tweet_classification_prompt
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.globals import set_verbose, set_debug


def get_tweet_sentiment(tweet_text: str, tokens: List[TokenInfo]) -> SentimentResponse:
    """Returns the sentiment of a tweet along with token information.

    Args:
        tweet_text (str): The text of the tweet.
        tokens (List[TokenInfo]): A list of token information.

    Returns:
        SentimentResponse: A response containing token information and the corresponding tweet sentiment.
    """

    # tokens_strs = [
    #     token.mint_address if token.mint_address else token.ticker for token in tokens
    # ]

    prompt = tweet_classification_prompt
    parser = PydanticOutputParser(
        pydantic_object=SentimentResponse,
    )
    llm = LLM().llm
    chain = (prompt | llm | parser).with_retry(
        stop_after_attempt=3,
        retry_if_exception_type=(OutputParserException, ValidationError),
    )

    sentiment = chain.invoke(
        {
            "tweet_text": tweet_text,
            "tokens": tokens,
            "parsing_model": SentimentResponse.model_json_schema(),
        }
    )

    return sentiment
