from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

Rating = Annotated[int, Field(gt=0, le=5)]


class Question(BaseModel):
    id: UUID | None
    question: str
    version: int
    rating: Rating

