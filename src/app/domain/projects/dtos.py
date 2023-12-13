from uuid import UUID

from lib.dto import BaseModel
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from pydantic import EmailStr

from .models import Project


class ProjectDTO(SQLAlchemyDTO[Project]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "updated_at",
            "managers",
            "groups",
        },
    )


class ProjectDetailDTO(SQLAlchemyDTO[Project]):
    config = SQLAlchemyDTOConfig(
        exclude={
            "updated_at",
            "managers.0.created_at",
            "managers.0.updated_at",
            "managers.0.is_system_admin",
            "managers.0.is_verified",
            "managers.0.password_hash",
            "managers.0.password_salt",
            "managers.0.managed_projects",
            "managers.0.joined_groups",
            "groups.0.project_id",
            "groups.0.project",
            "groups.0.members",
        },
    )


class ProjectCreateDTO(BaseModel):
    name: str
    description: str
    managers: list[EmailStr] | None = None


ProjectUsersAddDTO = list[EmailStr]
ProjectUsersRemoveDTO = list[UUID]


class ProjectUpdateDTO(BaseModel):
    name: str | None
    description: str | None
