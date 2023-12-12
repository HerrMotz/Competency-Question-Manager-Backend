from uuid import UUID

from app.domain.rating.models import IndividualRating
from app.lib.dto import BaseModel


class RatingDTO(BaseModel):
    id: UUID | None = None
    rating: IndividualRating
    question_id: UUID
    user_id: UUID | None = None
