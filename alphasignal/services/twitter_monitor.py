import re
from typing import Dict, Any, List, Tuple
import uuid
from datetime import datetime, timezone


from alphasignal.database.db import SQLiteDB
from alphasignal.models.token_info import TokenInfo
from alphasignal.models.tweet_data_extraction import ExtractedTweetData
from alphasignal.services.profile_manager import ProfileManager
from alphasignal.models.tweet_catcher_payload import TweetCatcherWebhookPayload
from alphasignal.models.tweet import Tweet
from alphasignal.models.event import Event
from alphasignal.models.enums import Platform, TweetSentiment, TweetType


class TwitterMonitor:
    def __init__(self):
        self.db = SQLiteDB()
        self.profile_manager = ProfileManager()

    def _find_tickers(self, message: str) -> List[TokenInfo]:
        """Returns all matches for stock tickers in the text."""
        ticker_pattern = re.compile(r"\$[A-Za-z]{1,5}")
        tickers = ticker_pattern.findall(message)
        return [TokenInfo(ticker=ticker) for ticker in tickers]

    def _find_solana_addresses(self, message: str) -> List[TokenInfo]:
        """Returns all matches for potential Solana wallet addresses."""
        solana_pattern = re.compile(r"[1-9A-HJ-NP-Za-km-z]{32,44}")
        addresses = solana_pattern.findall(message)
        return [TokenInfo(mint_address=address) for address in addresses]

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
                Platform.TWITTER.value, tweetPayload.task.user
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

        # Add extracted tweet data to the database
        tokens = [token.dict() for token in extracted_data.tokens]
        token_sentiments = [
            {"token_info": token_info.dict(), "sentiment": sentiment.value}
            for token_info, sentiment in extracted_data.token_sentiment
        ]
        self.db.add_extracted_tweet_data(
            tweet_id=tweet_id,
            tweet_type=extracted_data.tweet_type.value,
            tokens=tokens,
            token_sentiment=token_sentiments,
        )

    def _classify_tokens_sentiment(
        self, token: str, tweet_text: str
    ) -> List[Tuple[TokenInfo, TweetSentiment]]:
        # Placeholder for sentiment classification logic
        # You can replace this with actual sentiment analysis using an LLM
        pass

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
        message = tweetPayload.data.full_text or tweetPayload.data.text or ""

        # Extract tickers and Solana addresses
        tickers = self._find_tickers(message)
        solana_addresses = self._find_solana_addresses(message)

        # Combine tickers and Solana addresses into a single list of TokenInfo
        tokens = tickers + solana_addresses

        # Classify sentiment for tokens
        token_sentiments = []
        if tokens != []:
            token_sentiments = self._classify_tokens_sentiment(tickers)

        return ExtractedTweetData(
            tweet_type=tweet_type,
            tokens=tokens,
            token_sentiment=token_sentiments,
        )

    def process_tweet_webhook(self, tweetPayload: TweetCatcherWebhookPayload) -> None:
        """
        Processes the incoming webhook payload from the TweetCatcher service.
        """
        # perform data extraction and sentiment classification
        extracted_data = self._extract_tweet_info(tweetPayload)

        # action on extracted data
        ...

        # add to db
        self._add_tweet_event_to_db(tweetPayload, extracted_data)
