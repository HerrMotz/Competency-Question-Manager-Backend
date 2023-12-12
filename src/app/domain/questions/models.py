from uuid import UUID

from lib.dto import BaseModel
from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from ..rating.dtos import RatingDTO


class QuestionOverviewDTO(BaseModel):
    id: UUID
    question: str
    rating: int | None = None
    author_id: UUID
    author_name: str


class QuestionDetailDTO(BaseModel):
    id: UUID
    question: str
    ratings: list[RatingDTO]
    author_name: str
    author_id: UUID


class QuestionCreateDTO(BaseModel):
    question: str


class QuestionCreatedDTO(BaseModel):
    id: UUID
    question: str
    author_id: UUID


class QuestionUpdateDTO(BaseModel):
    question: str


class QuestionUpdatedDTO(BaseModel):
    id: UUID
    question: str
    author_id: UUID


class Question(UUIDAuditBase):
    question: Mapped[str]
    author_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    author = relationship("User", back_populates="questions")
    ratings: Mapped[list["Rating"]] = relationship(back_populates="question")
