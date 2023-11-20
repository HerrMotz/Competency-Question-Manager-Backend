from uuid import UUID

from pydantic import BaseModel


class Question(BaseModel):
    id: UUID | None
    question: str
    version: int
