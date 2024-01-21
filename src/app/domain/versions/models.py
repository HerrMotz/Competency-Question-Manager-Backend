from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from sqlalchemy import Column, Table
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.schema import ForeignKey

if TYPE_CHECKING:
    from domain.questions.models import Question


VersionQuestions = Table(
    "version_questions",
    UUIDAuditBase.metadata,
    Column[UUID]("version_id", ForeignKey("version.id"), primary_key=True),
    Column[UUID]("question_id", ForeignKey("question.id"), primary_key=True),
)


class Version(UUIDAuditBase):
    questions: Mapped[list[Question]] = relationship(
        secondary="version_questions", back_populates="versions"
    )
