from typing import Any
from uuid import UUID, uuid4

from litestar import Controller, post, Request, get
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Rating
from .dtos import RatingDTO
from .services import RatingService
from ..accounts.models import User


class RatingController(Controller):
    path = "/ratings"
    service = RatingService()

    @post("/")
    async def set_rating(self, data: RatingDTO, session: AsyncSession, request: Request[User, Any, Any]) -> RatingDTO:
        return await self.service.set_rating(
            session=session,
            rating=RatingDTO(rating=data.rating, user_id=request.user.id, question_id=data.question_id),
        )

    @get(path="/")
    async def get_rating(self, session: AsyncSession, user_id: UUID, question_id: UUID) -> list[RatingDTO]:
        return await self.service.get_rating(user_id=user_id, question_id=question_id, session=session)
