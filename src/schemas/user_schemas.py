from typing import Annotated

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
)

from src.schemas.mixins import PasswordMixin, PasswordOptionalMixin

PhoneNumber = Annotated[str, Field(pattern=r"^\+?[1-9]\d{1,14}$")]


class UserCreateSchema(PasswordMixin):
    first_name: str = Field(min_length=1, max_length=255)
    middle_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone_number: Annotated[
        PhoneNumber,
        Field(min_length=12, max_length=12, description="+7 XXX XXX-XX-XX"),
    ]
    password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)


class UserUpdateSchema(PasswordOptionalMixin):
    first_name: str | None = Field(min_length=1, max_length=255, default=None)
    middle_name: str | None = Field(min_length=1, max_length=255, default=None)
    last_name: str | None = Field(min_length=1, max_length=255, default=None)
    email: EmailStr | None = Field(default=None)
    phone_number: (
        Annotated[PhoneNumber, Field(min_length=12, max_length=12)] | None
    ) = Field(default=None, description="+7 XXX XXX-XX-XX")
    password: str | None = Field(min_length=8, default=None)
    confirm_password: str | None = Field(min_length=8, default=None)


class UserDataResponseSchema(BaseModel):
    id: int
    first_name: str = Field(min_length=1, max_length=255)
    middle_name: str = Field(min_length=1, max_length=255)
    last_name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    phone_number: str


class UserCreateResponseSchema(BaseModel):
    message: str
    data: UserDataResponseSchema


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class TokenData(BaseModel):
    user_id: int
    email: str
    role: str
