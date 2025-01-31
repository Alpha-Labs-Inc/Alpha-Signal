import re
from enum import Enum
from typing import Dict, Any

from alphasignal.models.tweet_webhook import TweetType, WebhookData


class TwitterMonitor:
    def __init__(self):
        # Regex pattern for stock tickers prefixed by '$'
        self.ticker_pattern = re.compile(r"\$[A-Za-z]{1,5}")
        # Regex pattern for Solana addresses (32 to 44 length base58 string)
        self.solana_pattern = re.compile(r"[1-9A-HJ-NP-Za-km-z]{32,44}")

    def find_tickers(self, message: str):
        """Returns all matches for stock tickers in the text."""
        return self.ticker_pattern.findall(message)

    def find_solana_addresses(self, message: str):
        """Returns all matches for potential Solana wallet addresses."""
        return self.solana_pattern.findall(message)

    def determine_tweet_type(self, tweet_data: Dict[str, Any]) -> TweetType:
        """
        A helper function to classify the tweet as a retweet, reply, or post
        based on boolean flags within the tweet data.
        """
        is_retweet = tweet_data.get("is_retweet", False)
        is_reply = tweet_data.get("is_reply", False)

        if is_retweet:
            return TweetType.RETWEET
        elif is_reply:
            return TweetType.REPLY
        else:
            return TweetType.POST

    def handle_webhook(self, tweet_data: WebhookData):
        """
        1) Determine if this tweet is a Retweet, Reply, or a Post using the helper function.
        2) Extract the main text to parse out tickers and Solana addresses.
        3) Return structured data for further processing.
        """
        # Determine the tweet type using the helper function
        tweet_type = self.determine_tweet_type(tweet_data.dict())

        # Use 'full_text' if available; fallback to 'text'
        message = tweet_data.full_text or tweet_data.text or ""

        # Extract tickers and Solana addresses
        tickers = self.find_tickers(message)
        solana_addresses = self.find_solana_addresses(message)

        # Return a structure containing everything you need for further processing
        return {
            "type": tweet_type.value,
            "message": message,
            "tickers": tickers,
            "solana_addresses": solana_addresses,
            "user": tweet_data.user.dict()
            if tweet_data.user
            else {},  # Example: user data, screen_name, etc.
            "raw_data": tweet_data.dict(),  # You could include the whole tweet data if needed
        }
