from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .dtos import RatingGetDTO, RatingSetDTO
from .models import Rating


class RatingService:
    async def set_rating(self, session: AsyncSession, rating: RatingSetDTO, user_id: UUID) -> RatingSetDTO:
        """
        Set the ratings for a specific model and save it to the database.

        :param user_id:
        :param rating: RatingSetDTO
        :param session: AsyncSession
        :return: The saved ratings.
        :rtype: RatingSetDTO
        """
        if rating_from_db := await session.scalar(
            select(Rating).where(Rating.user_id == user_id).where(Rating.question_id == rating.question_id)
        ):
            rating_from_db.rating = rating.rating
            return RatingSetDTO.model_validate(rating_from_db)
        else:
            new_rating = Rating(id=uuid4(), rating=rating.rating, user_id=user_id, question_id=rating.question_id)
            session.add(new_rating)
            return RatingSetDTO.model_validate(new_rating)

    async def get_ratings(self, session: AsyncSession, question_id: UUID) -> list[RatingGetDTO]:
        """
        Get the list of ratings for a given question ID.

        :param session:
        :param question_id: The unique ID of the question.
        :type question_id: UUID
        :return: The list of ratings for the question.
        :rtype: list[RatingGetDTO]
        """
        ratings = await session.scalars(
            select(Rating).where(Rating.question_id == question_id).options(selectinload(Rating.user))
        )
        return [RatingGetDTO.model_copy(rating, update={"user_name": rating.user.name}) for rating in ratings]

    async def get_rating(self, session: AsyncSession, user_id: UUID, question_id: UUID) -> RatingGetDTO | None:
        rating = await session.scalar(
            select(Rating)
            .where(Rating.user_id == user_id)
            .where(Rating.question_id == question_id)
            .options(selectinload(Rating.user))
        )
        if rating:
            return RatingGetDTO(
                rating=rating.rating,
                question_id=rating.question_id,
                user_id=rating.user_id,
                user_name=rating.user.name,
            )

        else:
            return None
