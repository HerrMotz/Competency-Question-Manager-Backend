from uuid import UUID

from lib.dto import BaseModel

from .models import IndividualRating


class RatingSetDTO(BaseModel):
    rating: IndividualRating
    question_id: UUID

class RatingGetDTO(BaseModel):
    rating: IndividualRating
    question_id: UUID
    user_id: UUID
    user_name: str
