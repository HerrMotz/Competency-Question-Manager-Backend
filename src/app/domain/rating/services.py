from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_

from .models import Rating
from .dtos import RatingDTO


class RatingService:
    async def set_rating(self, session: AsyncSession, rating: RatingDTO) -> RatingDTO:
        """
        Set the rating for a specific model and save it to the database.

        :param rating: RatingDTO
        :param session: AsyncSession
        :return: The saved rating.
        :rtype: RatingDTO
        """
        if ratingFromDB := await session.scalar(
            select(Rating).where(Rating.user_id == rating.user_id).where(Rating.question_id == rating.question_id)
        ):
            ratingFromDB.rating = ratingFromDB.rating
            return RatingDTO.model_validate(rating)
        else:
            rating = Rating(id=uuid4(), user_id=rating.user_id, question_id=rating.question_id, rating=rating.rating)
            session.add(rating)
            return RatingDTO.model_validate(rating)

    async def get_ratings(self, session: AsyncSession, question_id: UUID) -> list[RatingDTO]:
        """
        Get the list of ratings for a given question ID.

        :param question_id: The unique ID of the question.
        :type question_id: UUID
        :return: The list of ratings for the question.
        :rtype: list[RatingDTO]
        """
        ratings = await session.scalars(select(Rating).where(Rating.question_id == question_id))
        return [RatingDTO.model_validate(rating) for rating in ratings]

    async def get_rating(self, session: AsyncSession, user_id: UUID, question_id: UUID) -> RatingDTO | None:

        rating = await session.scalar(
            select(Rating).where(Rating.user_id == user_id).where(Rating.question_id == question_id)
        )
        if rating:
            return RatingDTO.model_validate(rating)

        else:
            return None
