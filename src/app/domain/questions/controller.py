import math
from typing import Any
from uuid import UUID, uuid4

from litestar import Controller, Request, delete, get, post
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..accounts.models import User
from ..rating.dtos import RatingGetDTO
from ..rating.models import IndividualRating, Rating
from ..rating.services import RatingService
from .models import (
    Question,
    QuestionCreatedDTO,
    QuestionCreateDTO,
    QuestionDetailDTO,
    QuestionOverviewDTO,
)


class QuestionController(Controller):
    path = "/questions/"
    rating_service = RatingService()

    @post("/", status_code=HTTP_201_CREATED)
    async def create_question(
        self, session: AsyncSession, data: QuestionCreateDTO, request: Request[User, Any, Any]
    ) -> QuestionCreatedDTO:
        """
        Creates a question in the session.

        :param session: The session object to use for database operations.
        :param data: The question data to be created.
        :return: The created question data.
        """
        question = Question(id=uuid4(), question=data.question, author_id=request.user.id)
        session.add(question)
        return QuestionCreatedDTO.model_validate(question)

    @get("/", status_code=HTTP_200_OK)
    async def get_questions(self, session: AsyncSession) -> list[QuestionOverviewDTO]:
        """
        :param session: AsyncSession object used to execute the database query and retrieve questions.
        :return: A list of QuestionDTO objects representing the retrieved questions.
        """
        questions = await session.scalars(
            select(Question).options(selectinload(Question.author)).options(selectinload(Question.ratings))
        )
        question_dtos = [
            QuestionOverviewDTO(
                id=q.id,
                question=q.question,
                author_id=q.author_id,
                author_name=q.author.name,
                rating=sum([rating.rating for rating in q.ratings]) / len(q.ratings) if len(q.ratings) > 0 else 0,
            )
            for q in questions.all()
        ]
        return question_dtos

    @get(path="/{question_id:uuid}", status_code=HTTP_200_OK)
    async def get_question(self, session: AsyncSession, question_id: UUID) -> QuestionDetailDTO:
        """
        Retrieves a question by its ID.

        :param session: An `AsyncSession` object representing the database session.
        :param question_id: A `UUID` object representing the ID of the question to retrieve.
        :return: A `QuestionDTO` object containing the retrieved question.
        :raises HTTPException: If the question with the specified ID is not found.
        """
        q = (
            await session.execute(
                select(Question)
                .where(Question.id == question_id)
                .options(selectinload(Question.author))
                .options(selectinload(Question.ratings).options(selectinload(Rating.user)))
            )
        ).scalar()

        if not q:
            raise HTTPException(status_code=404, detail="Question not found")
        question_dto = QuestionDetailDTO(
            id=q.id,
            question=q.question,
            ratings=[
                RatingGetDTO(
                    rating=rating.rating,
                    user_id=rating.user_id,
                    user_name=rating.user.name,
                    question_id=rating.question_id,
                )
                for rating in q.ratings
            ],
            author_id=q.author_id,
            author_name=q.author.name,
        )
        return question_dto

    @delete(path="/{question_id:uuid}", status_code=HTTP_204_NO_CONTENT)
    async def delete_question(self, session: AsyncSession, question_id: UUID) -> None:
        """
        Deletes a question from the database.

        :param session: The async session used to interact with the database.
        :param question_id: The UUID of the question to be deleted.
        :return: None

        :raises HTTPException: If the question with the specified ID is not found.
        """
        question = await session.execute(select(Question).where(Question.id == question_id))
        if not question.scalar():
            raise HTTPException(status_code=404, detail="Question not found")
        await session.delete(question.scalar())
        await session.commit()
