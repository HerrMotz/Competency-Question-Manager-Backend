from uuid import UUID

from pydantic import BaseModel

from ..rating.models import Rating


class Question(BaseModel):
    id: UUID | None = None
    question: str | None = None
    version: int | None = None
    rating: Rating | None = None
