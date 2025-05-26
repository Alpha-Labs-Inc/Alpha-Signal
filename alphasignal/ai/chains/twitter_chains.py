from pydantic import ValidationError
from alphasignal.ai.llm import LLM
from alphasignal.ai.models.sentiment_response import SentimentResponse
from alphasignal.models.token_info import TokenInfo
from typing import List
from alphasignal.ai.prompts.twitter_prompts import tweet_classification_prompt
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from langchain_core.globals import set_verbose, set_debug
import logging


# Enable debug/verbose logging for the chain
set_verbose(True)
set_debug(True)

logger = logging.getLogger(__name__)


def get_tweet_sentiment(tweet_text: str, tokens: List[TokenInfo]) -> SentimentResponse:
    """Returns the sentiment of a tweet along with token information."""
    prompt = tweet_classification_prompt
    parser = PydanticOutputParser(pydantic_object=SentimentResponse)
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

    # Log the raw output for debugging
    logger.debug("chain.invoke output: %s", sentiment.json())

    return sentiment
