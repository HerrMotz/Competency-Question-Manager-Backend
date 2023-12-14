from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship



if TYPE_CHECKING:
    from domain.questions.models import Question
    from domain.ratings.models import Rating
    from domain.comments.models import Comment


class User(UUIDAuditBase):
    email: Mapped[str] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[bytes] = mapped_column(LargeBinary(length=128))
    password_salt: Mapped[bytes] = mapped_column(LargeBinary(length=128))
    is_system_admin: Mapped[bool]
    is_verified: Mapped[bool]

    questions: Mapped[list[Question]] = relationship(back_populates="author")
    ratings: Mapped[list[Rating]] = relationship(back_populates="user")
    comments: Mapped[list[Comment]] = relationship(back_populates="author")

    # TODO: add relationships
    # projects: Mapped[list["Project"]] = relationship(back_populates="members")
    # groups: Mapped[list["Group"]] = relationship(back_populates="members")
    # comments: Mapped[list["Comment"]] = relationship(back_populates="author")
