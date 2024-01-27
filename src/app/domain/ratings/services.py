from uuid import UUID, uuid4

from litestar.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .dtos import RatingSet
from .models import Rating


class RatingService:
    async def set_rating(self, session: AsyncSession, data: RatingSet, author_id: UUID) -> Rating:
        """
        Set the ratings for a specific model and save it to the database.

        :param user_id:
        :param data: RatingSet
        :param session: AsyncSession
        :return: The saved ratings.
        :rtype: RatingSet
        """
        if rating := await session.scalar(
            select(Rating)
            .where(Rating.author_id == author_id)
            .where(Rating.question_id == data.question_id)
            .options(selectinload(Rating.author))
        ):
            rating.rating = data.rating
            session.add(rating)
            await session.commit()
            await session.refresh(rating)

        else:
            rating = Rating(id=uuid4(), rating=data.rating, author_id=author_id, question_id=data.question_id)
            session.add(rating)
            await session.commit()
            await session.refresh(rating)
            rating = await session.scalar(
                select(Rating)
                .where(Rating.author_id == author_id)
                .where(Rating.question_id == data.question_id)
                .options(selectinload(Rating.author))
            )

        return rating

    async def get_rating(self, session: AsyncSession, user_id: UUID, question_id: UUID) -> Rating:
        if rating := await session.scalar(
            select(Rating)
            .where(Rating.author_id == user_id)
            .where(Rating.question_id == question_id)
            .options(selectinload(Rating.author))
        ):
            return rating
        else:
            raise HTTPException(status_code=404, detail="Rating not found.")
