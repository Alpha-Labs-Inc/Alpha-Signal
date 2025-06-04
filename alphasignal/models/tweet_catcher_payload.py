# alphasignal/models/minimal_tweet_webhook.py
from pydantic import BaseModel, Field
from typing import List, Optional


class DataMinimal(BaseModel):
    full_text: Optional[str] = None
    text: Optional[str] = None
    is_retweet: bool
    is_reply: bool

    class Config:
        extra = "ignore"


class TaskMinimal(BaseModel):
    user: str

    class Config:
        extra = "ignore"


class TweetWebhookMinimal(BaseModel):
    task: TaskMinimal
    data: DataMinimal

    class Config:
        extra = "ignore"
