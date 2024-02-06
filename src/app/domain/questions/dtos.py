from uuid import UUID

from lib.dto import BaseModel
from litestar.contrib.pydantic.pydantic_dto_factory import PydanticDTO
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.dto import DTOConfig

from .models import Question
from domain.terms.dtos import AnnotationDTO



class QuestionOverviewDTO(SQLAlchemyDTO[Question]):
    config = SQLAlchemyDTOConfig(
        include={
            "id",
            "group.id",
            "group.name",
            "question",
            "rating",
            "author.id",
            "author.email",
            "author.name",
            "no_consolidations",
        },
        rename_strategy="camel",
    )


class QuestionDetailDTO(SQLAlchemyDTO[Question]):
    config = SQLAlchemyDTOConfig(
        max_nested_depth=3,
        include={
            "id",
            "question",
            "group_id",
            "version_number",
            "ratings.0.rating",
            "ratings.0.author.id",
            "ratings.0.author.email",
            "ratings.0.author.name",
            "aggregated_rating",
            "author.id",
            "author.email",
            "author.name",
            "editor.id",
            "editor.email",
            "editor.name",
            "group.id",
            "group.name",
            "group.project.id",
            "group.project.name",
            "comments.0.author.id",
            "comments.0.author.email",
            "comments.0.author.name",
            "comments.0.comment",
            "comments.0.created_at",
            "no_consolidations",
            "consolidations.0.id",
            "consolidations.0.name",
            "consolidations.0.no_questions",
            "consolidations.0.project.id",
            "consolidations.0.project.name",
            "consolidations.0.engineer.id",
            "consolidations.0.engineer.email",
            "consolidations.0.engineer.name",
            "consolidations.0.questions.0.id",
            "consolidations.0.questions.0.group_id",
            "consolidations.0.questions.0.question",
            "consolidations.0.questions.0.author.id",
            "consolidations.0.questions.0.author.email",
            "consolidations.0.questions.0.author.name",
            "versions.0.question_string",
            "versions.0.version_number",
            "versions.0.editor.id",
            "versions.0.editor.email",
            "versions.0.editor.name",
            "annotations.0.id",
            "annotations.0.content",
            "annotations.0.term.id",
            "annotations.0.term.content",

        },
        rename_strategy="camel",
    )


class QuestionCreate(BaseModel):
    question: str
    annotations: list[AnnotationDTO] = []


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
