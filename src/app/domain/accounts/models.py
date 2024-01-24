from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from domain.consolidations.models import Consolidation
    from domain.groups.models import Group
    from domain.projects.models import Project
    from domain.comments.models import Comment
    from domain.questions.models import Question
    from domain.ratings.models import Rating


class User(UUIDAuditBase):
    email: Mapped[str] = mapped_column(unique=True, index=True)
    name: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[bytes] = mapped_column(LargeBinary(length=128))
    password_salt: Mapped[bytes] = mapped_column(LargeBinary(length=128))
    is_system_admin: Mapped[bool]
    is_verified: Mapped[bool]

    managed_projects: Mapped[list[Project]] = relationship(secondary="project_managers", back_populates="managers")
    engineered_projects: Mapped[list[Project]] = relationship(
        secondary="project_engineers", back_populates="engineers"
    )
    joined_groups: Mapped[list[Group]] = relationship(secondary="group_members", back_populates="members")
    consolidations: Mapped[list[Consolidation]] = relationship(back_populates="engineer")
    questions: Mapped[list[Question]] = relationship(back_populates="author")
    ratings: Mapped[list[Rating]] = relationship(back_populates="author")
    comments: Mapped[list[Comment]] = relationship(back_populates="author")
