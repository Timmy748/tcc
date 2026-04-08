from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    username: str
    email: EmailStr


class UserPublicSchema(UserSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class UserListSchema(BaseModel):
    users: list[UserPublicSchema]


class CreateUserSchema(UserSchema):
    password: str


class UpdateUserSchema(BaseModel):
    username: str | None
    email: EmailStr | None
    password: str | None
