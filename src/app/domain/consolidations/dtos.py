from uuid import UUID

from lib.dto import BaseModel
from litestar.contrib.pydantic.pydantic_dto_factory import PydanticDTO
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.dto import DTOConfig

from .models import Consolidation


class ConsolidationDTO(SQLAlchemyDTO[Consolidation]):
    config = SQLAlchemyDTOConfig(
        rename_strategy="camel",
        exclude={
            "engineer.password_hash",
            "engineer.password_salt",
            "engineer.is_system_admin",
            "engineer.is_verified",
            "engineer.consolidations",
            "engineer.questions",
            "engineer.ratings",
            "question.ratings",
            "question.consolidations",
            "question.author_id",
            "question.author.password_hash",
            "question.author.password_salt",
            "question.author.is_system_admin",
            "question.author.is_verified",
            "question.author.consolidations",
            "question.author.questions",
            "question.author.ratings",
        },
    )


class ConsolidationCreate(BaseModel):
    question: str
    ids: list[UUID] | None = None


class ConsolidationCreateDTO(PydanticDTO[ConsolidationCreate]):
    config = DTOConfig(rename_strategy="camel")


class ConsolidationUpdate(BaseModel):
    question: str | None


class ConsolidationUpdateDTO(PydanticDTO[ConsolidationUpdate]):
    config = DTOConfig(rename_strategy="camel")


class MoveQuestion(BaseModel):
    ids: list[UUID]


class MoveQuestionDTO(PydanticDTO[MoveQuestion]):
    config = DTOConfig(rename_strategy="camel")
