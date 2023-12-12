from typing import Any
from uuid import UUID, uuid4

from litestar import Controller, Request, get, post
from sqlalchemy.ext.asyncio import AsyncSession

from ..accounts.models import User
from .dtos import RatingDTO
from .models import Rating
from .services import RatingService


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
