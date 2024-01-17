from uuid import UUID

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.contrib.pydantic import PydanticDTO
from litestar.dto import DTOConfig

from ...lib.dto import BaseModel

from .models import Comment


class CommentDTO(SQLAlchemyDTO[Comment]):
    config = SQLAlchemyDTOConfig(
        rename_strategy="camel",
        include={"id", "comment", "author_id", "question_id", "author.name", "created_at"},
    )


class CommentCreate(BaseModel):
    comment: str
    question_id: UUID


class CommentCreateDTO(PydanticDTO[CommentCreate]):
    config = DTOConfig(rename_strategy="camel")


class CommentGet(BaseModel):
    comment: str
    author_id: UUID
    question_id: UUID
    author_name: str


class CommentGetDTO(PydanticDTO[CommentGet]):
    config = DTOConfig(rename_strategy="camel")
