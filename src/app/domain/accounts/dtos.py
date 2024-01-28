from uuid import UUID

from lib.dto import BaseModel
from pydantic import EmailStr


class UserGetDTO(BaseModel):
    id: UUID
    email: EmailStr
    is_system_admin: bool
    is_verified: bool


class UserRegisterDTO(BaseModel):
    email: EmailStr
    password: str


class UserUpdateDTO(BaseModel):
    email: EmailStr | None = None
    password: str | None = None
    is_system_admin: bool | None = None
    is_verified: bool | None = None


class UserLoginDTO(BaseModel):
    email: str
    password: str


class UserAccessDTO(UserGetDTO):
    token: str | None = None
