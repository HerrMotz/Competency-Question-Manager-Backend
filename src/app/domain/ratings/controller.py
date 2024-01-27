from typing import Annotated, Any, TypeVar
from uuid import UUID

from litestar import Controller, Request, get, post
from litestar.enums import RequestEncodingType
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED
from sqlalchemy.ext.asyncio import AsyncSession

from ..accounts.models import User
from .dtos import RatingGetDTO, RatingSet, RatingSetDTO
from .models import Rating
from .services import RatingService

T = TypeVar("T")
JsonEncoded = Annotated[T, Body(media_type=RequestEncodingType.JSON)]


class RatingController(Controller):
    path = "/ratings"
    tags = ["Ratings"]
    service = RatingService()

    @post("/", dto=RatingSetDTO, return_dto=RatingGetDTO, status_code=HTTP_201_CREATED)
    async def set_rating(
        self, data: JsonEncoded[RatingSet], session: AsyncSession, request: Request[User, Any, Any]
    ) -> Rating:
        """Creates a new `Rating`"""
        return await self.service.set_rating(session=session, data=data, author_id=request.user.id)

    @get(path="/{question_id:uuid}/user/{user_id:uuid}", return_dto=RatingGetDTO, status_code=HTTP_200_OK)
    async def get_rating(self, session: AsyncSession, user_id: UUID, question_id: UUID) -> Rating:
        return await self.service.get_rating(user_id=user_id, question_id=question_id, session=session)
