import re
from enum import Enum
from typing import Dict, Any, List
import uuid
from datetime import datetime, timezone
from pydantic import BaseModel

from alphasignal.database.db import SQLiteDB
from alphasignal.services.profile_manager import ProfileManager
from alphasignal.models.tweet_catcher_payload import (
    TweetType,
    TweetCatcherWebhookPayload,
)
from alphasignal.models.tweet import Tweet
from alphasignal.models.event import Event
from alphasignal.models.enums import Platform


class TwitterMonitor:
    def __init__(self):
        self.db = SQLiteDB()
        self.profile_manager = ProfileManager()

    def _find_tickers(self, message: str):
        """Returns all matches for stock tickers in the text."""
        ticker_pattern = re.compile(r"\$[A-Za-z]{1,5}")
        return ticker_pattern.findall(message)

    def _find_solana_addresses(self, message: str):
        """Returns all matches for potential Solana wallet addresses."""
        solana_pattern = re.compile(r"[1-9A-HJ-NP-Za-km-z]{32,44}")
        return solana_pattern.findall(message)

    def _determine_tweet_type(self, tweetPayload: Dict[str, Any]) -> TweetType:
        """
        A helper function to classify the tweet as a retweet, reply, or post
        based on boolean flags within the tweet data.
        """
        is_retweet = tweetPayload.get("is_retweet", False)
        is_reply = tweetPayload.get("is_reply", False)

        if is_retweet:
            return TweetType.RETWEET
        elif is_reply:
            return TweetType.REPLY
        else:
            return TweetType.POST

    def _add_tweet_event_to_db(self, tweetPayload: TweetCatcherWebhookPayload):
        """
        Adds the tweet and corresponding event to the database.
        """
        tweet_id = str(uuid.uuid4())
        event_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc)

        tweet = Tweet(
            id=tweet_id,
            full_text=tweetPayload.data.full_text or tweetPayload.data.text or "",
            is_retweet=tweetPayload.data.is_retweet,
            is_reply=tweetPayload.data.is_reply,
            created_at=created_at,
        )

        if tweetPayload.data.user:
            profile_id = self.profile_manager.get_profile(
                Platform.TWITTER.value, tweetPayload.data.user.screen_name
            ).id

        event = Event(
            id=event_id,
            profile_id=profile_id,
            tweet_id=tweet_id,
            telegram_id=None,  # telegram_id is null
            time_processed=created_at,
        )

        self.db.add_tweet(tweet)
        self.db.add_event(event)

    def _classify_token_sentiment(self, token: str, tweet_text: str) -> Sentiment:
        # Placeholder for sentiment classification logic
        # You can replace this with actual sentiment analysis using an LLM
        return Sentiment.POSITIVE  # Example sentiment

    def _extract_tweet_info(
        self, tweetPayload: TweetCatcherWebhookPayload
    ) -> ExtractedData:
        """
        1) Determine if this tweet is a Retweet, Reply, or a Post using the helper function.
        2) Extract the main text to parse out tickers and Solana addresses.
        3) Classify sentiment for tickers and Solana addresses.
        4) Return structured data for further processing.
        """

        # Determine the tweet type using the helper function
        tweet_type = self._determine_tweet_type(tweetPayload.dict())
        message = tweetPayload.data.full_text or tweetPayload.text or ""

        # Extract tickers and Solana addresses
        tickers = self._find_tickers(message)
        solana_addresses = self._find_solana_addresses(message)

        # Classify sentiment for tickers and Solana addresses
        ticker_sentiment = {
            ticker: self._classify_token_sentiment(ticker, message)
            for ticker in tickers
        }
        solana_sentiment = {
            address: self._classify_token_sentiment(address, message)
            for address in solana_addresses
        }

        return ExtractedData(
            tickers=tickers,
            solana_addresses=solana_addresses,
            ticker_sentiment=ticker_sentiment,
            solana_sentiment=solana_sentiment,
        )

    def process_tweet_webhook(self, tweetPayload: TweetCatcherWebhookPayload) -> None:
        """
        Processes the incoming webhook payload from the TweetCatcher service.
        """
        extracted_data = self._extract_tweet_info(tweetPayload)

        # add to db
        self._add_tweet_event_to_db(tweetPayload)
