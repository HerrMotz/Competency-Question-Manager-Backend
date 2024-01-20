from uuid import UUID

from lib.dto import BaseModel, NonEmptyString
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from pydantic import EmailStr

from .models import Group


class GroupDTO(SQLAlchemyDTO[Group]):
    config = SQLAlchemyDTOConfig(
        include={
            "id",
            "name",
            "no_members",
            "no_questions" "created_at",
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
        max_nested_depth=2,
        include={
            "id",
            "name",
            "no_members",
            "no_questions",
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
            "questions.0.question",
            "questions.0.aggregated_rating",
            "questions.0.author.id",
            "questions.0.author.name",
            "questions.0.author.email",
        },
    )


class GroupCreateDTO(BaseModel):
    name: NonEmptyString
    project_id: UUID
    members: list[EmailStr] | None = None


class GroupUsersAddDTO(BaseModel):
    emails: list[EmailStr]


class GroupUsersRemoveDTO(BaseModel):
    ids: list[UUID]


class GroupUpdateDTO(BaseModel):
    name: NonEmptyString | None
