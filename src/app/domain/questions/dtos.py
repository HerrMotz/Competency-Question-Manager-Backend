from uuid import UUID

from lib.dto import BaseModel
from litestar.contrib.pydantic.pydantic_dto_factory import PydanticDTO
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.dto import DTOConfig

from .models import Question


class QuestionOverviewDTO(SQLAlchemyDTO[Question]):
    config = SQLAlchemyDTOConfig(include={"id", "question", "rating", "author.id", "author.name"})


class QuestionDetailDTO(SQLAlchemyDTO[Question]):
    config = SQLAlchemyDTOConfig(
        max_nested_depth=2,
        include={
            "id",
            "question",
            "ratings.rating",
            "ratings.user.id",
            "ratings.user.name",
            "aggregated_rating",
            "author.id",
            "author.name",
            "group.id",
            "group.name",
            "group.project.id",
            "group.project.name",
            "consolidations.0.id",
            "consolidations.0.name",
            "consolidations.0.no_questions",
            "versions.questions.id"
            "version"
        },
        rename_strategy="camel",
    )


class QuestionCreate(BaseModel):
    question: str


class QuestionCreateDTO(PydanticDTO[QuestionCreate]):
    config = DTOConfig(rename_strategy="camel")


class QuestionUpdate(BaseModel):
    question: str


class QuestionUpdateDTO(PydanticDTO[QuestionUpdate]):
    config = DTOConfig(rename_strategy="camel")


class QuestionUpdated(BaseModel):
    id: UUID
    question: str
    author_id: UUID


class QuestionUpdatedDTO(PydanticDTO[QuestionUpdated]):
    config = DTOConfig(rename_strategy="camel")
