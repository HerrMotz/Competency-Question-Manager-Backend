from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from pydantic import Field
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from domain.accounts.models import User
    from domain.questions.models import Question


IndividualRating = Annotated[int, Field(gt=0, le=5)]


class Rating(UUIDAuditBase):
    rating: Mapped[int]
    question_id: Mapped[UUID] = mapped_column(ForeignKey("question.id"))
    author_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))

    author: Mapped[User] = relationship(back_populates="ratings")
    question: Mapped[Question] = relationship(back_populates="ratings")
