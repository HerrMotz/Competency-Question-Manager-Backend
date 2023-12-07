from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, Field

IndividualRating = Annotated[int, Field(gt=0, le=5)]


class Rating(BaseModel):
    id: UUID | None = None
    rating: IndividualRating
    question_id: UUID
    user_id: UUID | None = None
    version: int
