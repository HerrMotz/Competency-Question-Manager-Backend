from uuid import UUID

from lib.dto import BaseModel
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from pydantic import EmailStr

from .models import Group


class GroupDTO(SQLAlchemyDTO[Group]):
    config = SQLAlchemyDTOConfig(
        include={
            "id",
            "name",
            "no_members",
            "created_at",
            "updated_at",
            "project.id",
            "project.name",
            "project.description",
            "project.created_at",
            "project.updated_at",
        },
    )


class GroupDetailDTO(SQLAlchemyDTO[Group]):
    config = SQLAlchemyDTOConfig(
        max_nested_depth=1,
        include={
            "id",
            "name",
            "no_members",
            "created_at",
            "updated_at",
            "project.id",
            "project.name",
            "project.description",
            "project.created_at",
            "project.updated_at",
            "members.0.id",
            "members.0.name",
            "members.0.email",
        },
    )


class GroupCreateDTO(BaseModel):
    name: str
    project_id: UUID
    members: list[EmailStr] | None = None


class GroupUsersAddDTO(BaseModel):
    emails: list[EmailStr]


class GroupUsersRemoveDTO(BaseModel):
    ids: list[UUID]


class GroupUpdateDTO(BaseModel):
    name: str | None
