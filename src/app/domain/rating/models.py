from typing import Annotated
from uuid import UUID

from advanced_alchemy.base import UUIDAuditBase
from lib.dto import BaseModel
from pydantic import Field
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

IndividualRating = Annotated[int, Field(gt=0, le=5)]


class RatingDTO(BaseModel):
    id: UUID | None = None
    rating: IndividualRating
    question_id: UUID
    user_id: UUID | None = None


class Rating(UUIDAuditBase):
    rating: Mapped[int]
    question_id: Mapped[UUID] = mapped_column(ForeignKey("question.id"))
    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    user = relationship("User", back_populates="ratings")
    question = relationship("Question", back_populates="ratings")

