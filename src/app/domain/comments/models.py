from __future__ import annotations

from uuid import UUID
from typing import TYPE_CHECKING

from advanced_alchemy.base import UUIDAuditBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

if TYPE_CHECKING:
    from ..accounts.models import User
    from ..ratings.models import Question


class Comment(UUIDAuditBase):
    comment: Mapped[str]
    question_id: Mapped[UUID] = mapped_column(ForeignKey("question.id"))
    author_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))

    author: Mapped[User] = relationship(back_populates="comments")
    question: Mapped[Question] = relationship(back_populates="comments")
