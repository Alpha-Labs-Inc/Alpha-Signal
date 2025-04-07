from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class UserInfo(BaseModel):
    id: int
    id_str: str
    name: str
    screen_name: str
    entities: Dict[str, Any]
    created_at: datetime
    statuses_count: int
    profile_background_color: Optional[str] = None
    profile_image_url: Optional[str] = None
    profile_image_url_https: Optional[str] = None
    profile_link_color: Optional[str] = None
    profile_sidebar_border_color: Optional[str] = None
    profile_sidebar_fill_color: Optional[str] = None
    profile_text_color: Optional[str] = None
    profile_use_background_image: Optional[bool] = None
    has_extended_profile: Optional[bool] = None
    default_profile: Optional[bool] = None
    can_media_tag: Optional[bool] = None
    advertiser_account_type: Optional[str] = None
    analytics_type: Optional[str] = None
    business_profile_state: Optional[str] = None
    translator_type: Optional[str] = None

    @validator("created_at", pre=True)
    def parse_created_at(cls, value):
        return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y")


class Task(BaseModel):
    user: str
    userInfo: UserInfo
    reason: str
    taskId: int
    group: str


class Entities(BaseModel):
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


class Verification(BaseModel):
    is_blue_verified: bool
    verified_type: Optional[str] = None


class DataUser(BaseModel):
    id_str: str
    screen_name: str
    name: str
    image: str
    verification: Optional[Verification] = None


class TweetStatus(BaseModel):
    id_str: Optional[str] = None
    full_text: str
    entities: Optional[Entities] = None
    extended_entities: Optional[ExtendedEntities] = None
    user: Optional[DataUser] = None


class WebhookData(BaseModel):
    id_str: str
    created_at: datetime
    full_text: Optional[str] = None
    text: Optional[str] = None
    entities: Optional[Entities] = None
    extended_entities: Optional[ExtendedEntities] = None
    user: Optional[DataUser] = None
    is_retweet: bool
    is_reply: bool
    retweeted_status: Optional[TweetStatus] = None
    reply_status: Optional[TweetStatus] = None

    @validator("created_at", pre=True)
    def parse_created_at(cls, value):
        return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y")


class TweetCatcherWebhookPayload(BaseModel):
    task: Task
    data: WebhookData
