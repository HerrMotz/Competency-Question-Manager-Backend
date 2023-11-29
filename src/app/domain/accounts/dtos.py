import dataclasses
from typing import Any, Self
from uuid import UUID


@dataclasses.dataclass
class FromDictMixin:
    @classmethod
    def from_dict(cls, **kwargs: dict[str, Any]) -> Self:
        names = {field.name for field in dataclasses.fields(cls)}
        arguments = {key: value for key, value in kwargs.items() if key in names}
        return cls(**arguments)


@dataclasses.dataclass
class UserRegisterDTO(FromDictMixin):
    email: str
    name: str
    password: str


@dataclasses.dataclass
class UserGetDTO(FromDictMixin):
    id: UUID
    email: str
    name: str
    is_system_admin: bool
    is_verified: bool


@dataclasses.dataclass
class UserUpdateDTO(FromDictMixin):
    email: str | None = None
    name: str | None = None
    password: str | None = None
    is_system_admin: bool | None = None
    is_verified: bool | None = None


@dataclasses.dataclass
class UserLoginDTO(FromDictMixin):
    email: str
    password: str
