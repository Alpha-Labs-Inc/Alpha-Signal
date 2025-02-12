from pydantic import BaseModel, Field
from datetime import datetime


class Event(BaseModel):
    id: str
    profile_id: str
    full_text: str
    tweet_id: str
    telegram_id: str
    time_processed: datetime = Field(default_factory=lambda: datetime.now().isoformat())
