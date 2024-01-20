from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.schema import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property

if TYPE_CHECKING:
    from domain.accounts.models import User
    from domain.projects.models import Project
    from domain.questions.models import Question


ConsolidatedQuestions = Table(
    "consolidated_questions",
    UUIDAuditBase.metadata,
    Column[UUID]("consolidation_id", ForeignKey("consolidation.id"), primary_key=True),
    Column[UUID]("question_id", ForeignKey("question.id"), primary_key=True),
)


class Consolidation(UUIDAuditBase):
    name: Mapped[str] = mapped_column(unique=True)
    engineer_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"))
    project_id: Mapped[UUID] = mapped_column(ForeignKey("project.id"))

    project: Mapped[Project] = relationship(back_populates="consolidations")
    engineer: Mapped[User] = relationship(back_populates="consolidations")
    questions: Mapped[list[Question]] = relationship(
        secondary="consolidated_questions", back_populates="consolidations"
    )

    @hybrid_property
    def no_questions(self) -> int:
        return len(self.questions)
