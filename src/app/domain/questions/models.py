from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from lib.dto import BaseModel
from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..comments.dtos import CommentGet
from ..ratings.dtos import RatingGetDTO

if TYPE_CHECKING:
    from ..accounts.models import User
    from ..ratings.models import Rating
    from ..comments.models import Comment


class QuestionOverviewDTO(BaseModel):
    id: UUID
    question: str
    rating: int | None = None
    author_id: UUID
    author_name: str


class QuestionDetailDTO(BaseModel):
    id: UUID
    question: str
    ratings: list[RatingGetDTO]
    rating: int
    author_name: str
    author_id: UUID
    comments: list[CommentGet]


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

    author: Mapped[User] = relationship(back_populates="questions")
    ratings: Mapped[list[Rating]] = relationship(back_populates="question", cascade="all, delete-orphan")
    comments: Mapped[list[Comment]] = relationship(back_populates="question", cascade="all, delete-orphan")
