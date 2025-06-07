from fastapi import APIRouter
from alphasignal.models.tweet_catcher_payload import TweetWebhookMinimal
from alphasignal.services.twitter_monitor import TwitterMonitor

router = APIRouter()

twitter_monitor = TwitterMonitor()


@router.post("/webhooks/tweetcatcher/tweet-process", response_model=bool)
async def process_tweet_webhook(body: TweetWebhookMinimal) -> bool:
    """
    Process a tweet webhook payload from TweetCatcher.

    Args:
        tweetPayload (TweetCatcherWebhookPayload): The webhook payload received from TweetCatcher.

    Returns:
        bool: True if the tweet was successfully processed
    """
    return await twitter_monitor.process_tweet_webhook(body)
