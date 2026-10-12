from datetime import datetime, timezone
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


class SmrListResponse(BaseModel):
    smrs: list[SmrOut]


class SmrLike(BaseModel):
    action: int = Field(...)
