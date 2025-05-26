import re
from typing import List
import uuid
from datetime import datetime, timezone
import logging

from alphasignal.ai.chains.twitter_chains import get_tweet_sentiment
from alphasignal.ai.models.sentiment_response import SentimentResponse, TokenSentiment
from alphasignal.database.db import ProfileNotFoundError, SQLiteDB
from alphasignal.models.token_info import TokenInfo
from alphasignal.models.tweet_data_extraction import ExtractedTweetData
from alphasignal.services.auto_manager import AutoManager
from alphasignal.models.tweet_catcher_payload import TweetCatcherWebhookPayload
from alphasignal.models.tweet import Tweet
from alphasignal.models.event import Event
from alphasignal.models.enums import Platform, TweetSentiment, TweetType
from alphasignal.services.profile_manager import ProfileManager
from alphasignal.apis.dexscreener.dexscreener_client import DexscreenerClient


class TwitterMonitor:
    def __init__(self):
        self.db = SQLiteDB()
        self.profile_manager = ProfileManager()
        self.auto_manager = AutoManager()
        self.dexscreener_client = DexscreenerClient()

    def _find_tickers(self, message: str) -> List[TokenInfo]:
        """Returns all matches for stock tickers in the text."""
        ticker_pattern = re.compile(r"\$[A-Za-z]{1,15}")
        tickers = ticker_pattern.findall(message)
        return [
            TokenInfo(ticker=ticker, mint_address=None, name=None, image=None)
            for ticker in tickers
        ]

    def _find_mint_addresses(self, message: str) -> List[TokenInfo]:
        """Returns all matches for potential Solana mint addresses."""
        solana_pattern = re.compile(r"[1-9A-HJ-NP-Za-km-z]{32,44}")
        addresses = solana_pattern.findall(message)
        return [
            TokenInfo(mint_address=address, ticker=None, name=None, image=None)
            for address in addresses
        ]

    def _determine_tweet_type(
        self, tweetPayload: TweetCatcherWebhookPayload
    ) -> TweetType:
        """
        A helper function to classify the tweet as a retweet, reply, or post
        based on boolean flags within the tweet data.
        """
        is_retweet = tweetPayload.data.is_retweet
        is_reply = tweetPayload.data.is_reply

        if is_retweet:
            return TweetType.RETWEET
        elif is_reply:
            return TweetType.REPLY
        else:
            return TweetType.POST

    def _add_tweet_event_to_db(
        self,
        tweetPayload: TweetCatcherWebhookPayload,
        extracted_data: ExtractedTweetData,
    ) -> None:
        """
        Adds the tweet and corresponding event to the database.
        """
        tweet_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()

        tweet = Tweet(
            id=tweet_id,
            full_text=tweetPayload.data.full_text or tweetPayload.data.text or "",
            is_retweet=tweetPayload.data.is_retweet,
            is_reply=tweetPayload.data.is_reply,
            created_at=created_at,
        )

        if tweetPayload.task.user:
            try:
                profile_id = self.profile_manager.get_profile(
                    Platform.TWITTER.value, tweetPayload.task.user
                ).id
            except ProfileNotFoundError:
                # If the profile does not exist, create a new one
                profile_id = self.profile_manager.add_profile(
                    platform=Platform.TWITTER,
                    username=tweetPayload.task.user,
                )
            except Exception as e:
                logging.error(f"Error retrieving profile: {e}")
                raise

        event = Event(
            id=event_id,
            profile_id=profile_id,
            tweet_id=tweet_id,
            telegram_id=None,
            time_processed=created_at,
        )

        self.db.add_tweet(tweet)
        self.db.add_event(event)

        # Add extracted tweet data to the database
        tokens = [token.model_dump() for token in extracted_data.tokens]
        token_sentiments = [
            {"token_info": ts.token.model_dump(), "sentiment": ts.sentiment}
            for ts in extracted_data.token_sentiment.response
        ]
        self.db.add_extracted_tweet_data(
            tweet_id=tweet_id,
            tweet_type=extracted_data.tweet_type.value,
            tokens=str(tokens),
            token_sentiment=str(token_sentiments),
        )

    def _classify_tokens_sentiment(
        self, tweet_text: str, tokens: List[TokenInfo]
    ) -> SentimentResponse:
        # Initialize the LLM
        token_sentiment = get_tweet_sentiment(tweet_text, tokens)
        return token_sentiment

    def _extract_tweet_info(
        self, tweetPayload: TweetCatcherWebhookPayload
    ) -> ExtractedTweetData:
        """
        1) Determine if this tweet is a Retweet, Reply, or a Post using the helper function.
        2) Extract the main text to parse out tickers and Solana addresses.
        3) Classify sentiment for tickers and Solana addresses.
        4) Return structured data for further processing.
        """

        # Determine the tweet type using the helper function
        tweet_type = self._determine_tweet_type(tweetPayload)
        full_text = tweetPayload.data.full_text or tweetPayload.data.text or ""

        # Extract tickers and Solana addresses
        tickers = self._find_tickers(full_text)
        solana_addresses = self._find_mint_addresses(full_text)

        # Combine tickers and Solana addresses into a single list of TokenInfo
        tokens = tickers + solana_addresses

        # Classify sentiment for tokens
        token_sentiments = []
        if tokens != []:
            token_sentiments = self._classify_tokens_sentiment(full_text, tokens)

        return ExtractedTweetData(
            tweet_type=tweet_type,
            tokens=tokens,
            token_sentiment=token_sentiments,
        )

    async def _find_mint_address_from_ticker(self, ticker: str) -> str:
        """
        A helper function to find the mint address of a token from its ticker.
        """
        if ticker.startswith("$"):
            ticker = ticker[1:]
        try:
            mint_address = await self.dexscreener_client.get_top_volume_mint_address(
                ticker
            )
            return mint_address
        except Exception as e:
            logging.error(f"Error finding mint address for ticker {ticker}: {e}")
            return ""

    async def process_tweet_webhook(
        self, tweetPayload: TweetCatcherWebhookPayload
    ) -> bool:
        """
        Processes the incoming webhook payload from the TweetCatcher service.

        Args:
            tweetPayload (TweetCatcherWebhookPayload): The incoming webhook payload.

        Returns:
            bool: True if the tweet was successfully processed
        """
        # debug log the incoming payload
        logging.debug("Received tweet payload: %s", tweetPayload)

        # perform data extraction and sentiment classification
        extracted_data = self._extract_tweet_info(tweetPayload)

        # debug log the extracted data
        logging.debug("Extracted tweet data: %s", extracted_data)

        # add to db
        self._add_tweet_event_to_db(tweetPayload, extracted_data)

        # if any token missing mint_address, update the model with the mint_address
        for token in extracted_data.tokens:
            if not token.mint_address:
                token.mint_address = await self._find_mint_address_from_ticker(
                    token.ticker
                )

        # action on extracted data
        # TODO: currently only acts on a single token, need to update to handle multiple tokens
        if extracted_data.token_sentiment.response[0].sentiment == "positive":
            order = await self.auto_manager.auto_buy(
                extracted_data.tokens[0].mint_address,
                platform=Platform.TWITTER,
                username=tweetPayload.task.user,
            )
            if not order:
                raise Exception("Auto buy failed.")
        return True
