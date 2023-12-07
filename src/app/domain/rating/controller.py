from typing import Any
from uuid import UUID

from litestar import Controller, post, Request, get

from .models import Rating
from .services import RatingService
from ..accounts.models import User


class RatingController(Controller):
    path = "/ratings"
    service = RatingService()

    @post("/")
    async def create_rating(self, data: Rating, request: Request[User, Any, Any]) -> Rating:
        return await self.service.set_rating(data.model_copy(update={"user_id": request.user.id}))

    @get(path="/{question_id:uuid}")
    async def get_rating(self, question_id: UUID) -> list[Rating]:
        return await self.service.get_ratings(question_id)

