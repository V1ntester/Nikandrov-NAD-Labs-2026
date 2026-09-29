from pydantic import BaseModel, Field, ConfigDict


class UserBase(BaseModel):
    pass


class UserCreate(UserBase):
    username: str = Field(..., max_length=50)
    password: str = Field(..., max_length=255)


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str