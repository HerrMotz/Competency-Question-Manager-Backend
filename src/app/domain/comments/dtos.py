from uuid import UUID

from advanced_alchemy.extensions.litestar import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.contrib.pydantic import PydanticDTO
from litestar.dto import DTOConfig

from lib.dto import BaseModel

from .models import Comment


class CommentDTO(SQLAlchemyDTO[Comment]):
    config = SQLAlchemyDTOConfig(
        rename_strategy="camel",
        include={
            "comment",
            "author_id",
            "question_id",
        },
    )


class CommentGet(BaseModel):
    comment: str


class CommentGetDTO(PydanticDTO[CommentGet]):
    config = DTOConfig(rename_strategy="camel")
