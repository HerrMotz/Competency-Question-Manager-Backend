from uuid import UUID
from lib.dto import BaseModel

from litestar.contrib.sqlalchemy.base import UUIDAuditBase
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column

from ..rating.models import Rating


class QuestionDTO(BaseModel):
    id: UUID | None = None
    question: str
    version: int
    rating: Rating | None = None
    author_id: UUID | None = None


class Question(UUIDAuditBase):
    question: Mapped[str]
    version: Mapped[int]
    author_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'))
    author = relationship("User", back_populates="questions")
