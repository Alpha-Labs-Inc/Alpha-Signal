from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class Event(BaseModel):
    id: str
    profile_id: str
    tweet_id: Optional[str]
    telegram_id: Optional[str]
    time_processed: datetime = Field(default_factory=lambda: datetime.now().isoformat())
