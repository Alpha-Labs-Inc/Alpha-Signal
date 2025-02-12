from pydantic import BaseModel


class ProfileCreateRequest(BaseModel):
    platform: str
    username: str
