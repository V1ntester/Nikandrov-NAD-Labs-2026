from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class ReactorBase(BaseModel):
    pass


class ReactorCreate(ReactorBase):
    name: str = Field(..., max_length=100)
    manufacturer: str = Field(..., max_length=100)
    image_url: str = Field(..., max_length=1000)
    video_url: str = Field(..., max_length=1000)


class ReactorPublish(ReactorBase):
    description: str = Field(..., max_length=500)
    thermal_power: int = Field(...)
    electrical_power: int = Field(...)


class ReactorOut(ReactorBase):
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


class ReactorListResponse(BaseModel):
    reactors: list[ReactorOut]


class ReactorLike(BaseModel):
    action: int = Field(...)