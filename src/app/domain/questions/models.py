from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from domain.accounts.models import User
    from domain.consolidations.models import Consolidation
    from domain.rating.models import Rating


class Question(UUIDAuditBase):
    question: Mapped[str]
    author_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))

    author: Mapped[User] = relationship(back_populates="questions")
    ratings: Mapped[list[Rating]] = relationship(back_populates="question", cascade="all, delete-orphan")
    consolidations: Mapped[list[Consolidation]] = relationship(
        secondary="consolidated_questions", back_populates="questions"
    )

    @hybrid_property
    def aggregated_rating(self) -> int:
        return sum(map(lambda r: r.rating, self.ratings)) // len(self.ratings) if len(self.ratings) > 0 else 0
