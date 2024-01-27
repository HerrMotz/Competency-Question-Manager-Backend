from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey

if TYPE_CHECKING:
    from domain.questions.models import Question


class Version(UUIDAuditBase):
    question_string: Mapped[str]
    version_number: Mapped[int]

    question_id: Mapped[UUID] = mapped_column(ForeignKey("question.id"))
    question: Mapped[Question] = relationship(back_populates="versions")
