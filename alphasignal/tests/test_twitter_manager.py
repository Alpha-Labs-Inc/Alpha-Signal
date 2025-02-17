from alphasignal.ai.models.sentiment_response import SentimentResponse, TokenSentiment
from alphasignal.services.twitter_monitor import TwitterMonitor
from alphasignal.models.token_info import TokenInfo
from alphasignal.models.tweet_data_extraction import ExtractedTweetData
from alphasignal.models.enums import Platform, TweetSentiment, TweetType

# Language: Python


# Dummy classes to simulate tweetPayload structure
class DummyData:
    def __init__(self, full_text, text, is_retweet, is_reply):
        self.full_text = full_text
        self.text = text
        self.is_retweet = is_retweet
        self.is_reply = is_reply


class DummyTask:
    def __init__(self, user):
        self.user = user


class DummyPayload:
    def __init__(self, data, task):
        self.data = data
        self.task = task


# Fake auto_manager to record auto_buy calls
class FakeAutoManager:
    def __init__(self):
        self.calls = []

    def auto_buy(self, mint_address, platform, username):
        self.calls.append(
            {
                "mint_address": mint_address,
                "platform": platform,
                "username": username,
            }
        )


def test_process_tweet_webhook_calls_auto_buy():
    # Create a dummy token with a preset mint_address
    dummy_token = TokenInfo(
        ticker=None, mint_address="dummy_mint", name=None, image=None
    )
    # Create dummy extracted tweet data using the dummy token
    dummy_extracted_data = ExtractedTweetData(
        tweet_type=TweetType.POST,
        tokens=[dummy_token],
        token_sentiment=SentimentResponse(
            response=[
                TokenSentiment(token=dummy_token, sentiment=TweetSentiment.POSITIVE)
            ]
        ),
    )

    # Create a dummy tweet payload
    dummy_data = DummyData(
        full_text="This is a test tweet with $TEST and a Solana address abcdefghijklmnopqrstuvwxyz123456",
        text="Test tweet",
        is_retweet=False,
        is_reply=False,
    )
    dummy_task = DummyTask(user="testuser")
    dummy_payload = DummyPayload(data=dummy_data, task=dummy_task)

    # Instantiate TwitterMonitor
    monitor = TwitterMonitor()
    # Replace auto_manager with our fake
    fake_manager = FakeAutoManager()
    monitor.auto_manager = fake_manager

    # Monkey patch _extract_tweet_info to return our dummy_extracted_data
    monitor._extract_tweet_info = lambda payload: dummy_extracted_data
    # Monkey patch _add_tweet_event_to_db to do nothing (avoid DB calls)
    monitor._add_tweet_event_to_db = lambda payload, data: None

    # Call process_tweet_webhook
    monitor.process_tweet_webhook(dummy_payload)

    # Assert that auto_manager.auto_buy was called with expected parameters
    assert len(fake_manager.calls) == 1
    call = fake_manager.calls[0]
    assert call["mint_address"] == "dummy_mint"
    assert call["platform"] == Platform.TWITTER
    assert call["username"] == "testuser"


def test_find_tickers():
    monitor = TwitterMonitor()
    test_message = "This tweet mentions $AAPL and $GOOG."
    tickers = monitor._find_tickers(test_message)
    # Expect two tokens with tickers $AAPL and $GOOG
    expected = ["$AAPL", "$GOOG"]
    actual = [token.ticker for token in tickers]
    assert actual == expected


def test_find_mint_addresses():
    monitor = TwitterMonitor()
    # A dummy Solana mint address pattern (32 to 44 valid characters)
    test_message = "Mint address: 123456789ABCDEFGHJKLMNPQRSTUVWXYZab"
    addresses = monitor._find_mint_addresses(test_message)
    # Assert at least one address is found and mint_address is set
    assert len(addresses) >= 1
    for token in addresses:
        assert token.mint_address is not None
