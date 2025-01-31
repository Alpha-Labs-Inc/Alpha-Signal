from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class TweetType(Enum):
    POST = "post"
    REPLY = "reply"
    RETWEET = "retweet"


class UserInfo(BaseModel):
    advertiser_account_service_levels: List[str] = Field(default_factory=list)
    advertiser_account_type: str
    analytics_type: str
    blocked_by: bool
    blocking: bool
    can_dm: bool
    can_media_tag: bool
    created_at: str
    description: str
    entities: Dict[str, Any]
    fast_followers_count: int
    favourites_count: int
    follow_request_sent: bool
    followers_count: int
    followed_by: bool
    following: bool
    friends_count: int
    has_custom_timelines: bool
    has_extended_profile: bool
    is_translator: bool
    location: str
    media_count: int
    muting: bool
    name: str
    normal_followers_count: int
    notifications: bool
    pinned_tweet_ids_str: List[str] = Field(default_factory=list)
    profile_image_url_https: str
    profile_interstitial_type: str
    profile_link_color: str
    protected: bool
    screen_name: str
    statuses_count: int
    translator_type: str
    verified: bool
    withheld_in_countries: List[str] = Field(default_factory=list)


class Task(BaseModel):
    user: str
    userInfo: UserInfo
    reason: str
    taskId: int
    group: str


class Entities(BaseModel):
    # Expand these if you need more detail. Example includes just user_mentions.
    user_mentions: Optional[List[Dict[str, Any]]] = None
    hashtags: Optional[List[Dict[str, Any]]] = None
    symbols: Optional[List[Dict[str, Any]]] = None
    urls: Optional[List[Dict[str, Any]]] = None


class MediaVariant(BaseModel):
    content_type: str
    url: str
    bitrate: Optional[int] = None


class VideoInfo(BaseModel):
    aspect_ratio: List[int]
    duration_millis: int
    variants: List[MediaVariant]


class Media(BaseModel):
    additional_media_info: Optional[Dict[str, Any]] = None
    display_url: Optional[str] = None
    expanded_url: Optional[str] = None
    ext_media_availability: Optional[Dict[str, Any]] = None
    id_str: str
    indices: Optional[List[int]] = None
    media_key: str
    media_url_https: Optional[str] = None
    type: str
    url: Optional[str] = None
    video_info: Optional[VideoInfo] = None


class ExtendedEntities(BaseModel):
    media: List[Media]


class DataUser(BaseModel):
    screen_name: str
    name: str
    image: str


class TweetStatus(BaseModel):
    full_text: str
    entities: Optional[Entities] = None
    extended_entities: Optional[ExtendedEntities] = None
    user: Optional[DataUser] = None


class WebhookData(BaseModel):
    id_str: str
    created_at: str
    full_text: Optional[str] = None
    text: Optional[str] = None  # Some tweets may only have 'text'
    entities: Optional[Entities] = None
    extended_entities: Optional[ExtendedEntities] = None
    user: Optional[DataUser] = None
    is_retweet: bool
    is_reply: bool
    retweeted_status: Optional[TweetStatus] = None
    reply_status: Optional[TweetStatus] = None


class TweetCatcherWebhookPayload(BaseModel):
    task: Task
    data: WebhookData
