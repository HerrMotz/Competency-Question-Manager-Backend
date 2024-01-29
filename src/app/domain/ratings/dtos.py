from uuid import UUID

from lib.dto import BaseModel
from litestar.contrib.pydantic.pydantic_dto_factory import PydanticDTO
from litestar.contrib.sqlalchemy.dto import SQLAlchemyDTO, SQLAlchemyDTOConfig
from litestar.dto import DTOConfig

from .models import IndividualRating, Rating


class RatingGetDTO(SQLAlchemyDTO[Rating]):
    config = SQLAlchemyDTOConfig(
        include={"rating", "question_id", "author.id", "author.name"}, rename_strategy="camel"
    )


class RatingSet(BaseModel):
    rating: IndividualRating
    question_id: UUID


class RatingSetDTO(PydanticDTO[RatingSet]):
    config = DTOConfig(rename_strategy="camel")
