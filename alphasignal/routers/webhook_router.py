from fastapi import APIRouter
from alphasignal.models.tweet_catcher_payload import TweetCatcherWebhookPayload
from alphasignal.services.twitter_monitor import TwitterMonitor

router = APIRouter()

twitter_monitor = TwitterMonitor()


@router.post("/webhooks/tweetcatcher/tweet-process", response_model=bool)
async def process_tweet_webhook(tweetPayload: TweetCatcherWebhookPayload) -> None:
    """
    Process a tweet webhook payload from TweetCatcher.

    Args:
        tweetPayload (TweetCatcherWebhookPayload): The webhook payload received from TweetCatcher.

    Returns:
        bool: True if the tweet was successfully processed
    """
    res = await twitter_monitor.process_tweet_webhook(tweetPayload)
    return res
