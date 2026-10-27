from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class SmrBase(BaseModel):
    pass


class SmrCreate(SmrBase):
    name: str = Field(..., max_length=100)
    manufacturer: str = Field(..., max_length=100)
    image_url: str | None = Field(None, max_length=1000)
    video_url: str | None = Field(None, max_length=1000)


class SmrPublish(SmrBase):
    description: str = Field(..., max_length=500)
    thermal_power: int = Field(...)
    electrical_power: int = Field(...)


class SmrOut(SmrBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    manufacturer: str
    image_url: str | None
    video_url: str | None
    description: str | None
    thermal_power: int | None
    electrical_power: int | None
    status: str
    creator_id: int
    formed_at: datetime | None
    created_at: datetime


class SmrListItem(SmrOut):
    is_owner: bool = False
    is_liked: bool = False
    likes_count: int

    @classmethod
    def from_smr(cls, smr, user_id: int | None) -> "SmrListItem":
        obj = cls.model_validate(smr)
        obj.is_owner = user_id is not None and smr.creator_id == user_id
        obj.is_liked = bool(getattr(smr, "is_liked", False))
        obj.likes_count = int(getattr(smr, "likes_count", 0) or 0)
        return obj


class SmrListResponse(BaseModel):
    smrs: list[SmrListItem]


class SmrLike(BaseModel):
    action: int = Field(...)
