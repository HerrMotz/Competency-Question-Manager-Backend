from typing import Annotated
from uuid import UUID

from pydantic import Field
from lib.dto import BaseModel

from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped


Rating = Annotated[int, Field(gt=0, le=5)]


class QuestionDTO(BaseModel):
    id: UUID | None = None
    question: str
    version: int
    rating: Rating | None = None


class Question(UUIDAuditBase):
    question: Mapped[str]
    version: Mapped[int]