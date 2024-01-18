from typing import Annotated, Any, Sequence, TypeVar
from uuid import UUID, uuid4

from litestar import Controller, Request, delete, get, post
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .dtos import (
    QuestionCreate,
    QuestionCreateDTO,
    QuestionDetailDTO,
    QuestionOverviewDTO,
)
from .models import Question
from ..accounts.models import User
from ..rating.models import Rating

T = TypeVar("T")
JsonEncoded = Annotated[T, Body(media_type=RequestEncodingType.JSON)]


class QuestionController(Controller):
    path = "/questions/"
    tags = ["Questions"]

    @post("/", dto=QuestionCreateDTO, return_dto=QuestionDetailDTO, status_code=HTTP_201_CREATED)
    async def create_question(
        self, session: AsyncSession, data: JsonEncoded[QuestionCreate], request: Request[User, Any, Any]
    ) -> Question:
        """
        Creates a new `Question`

        :param request: Request[User, Any, Any]
        :param session: The session object to use for database operations.
        :param data: The question data to be created.
        :return: The created question data.
        """
        question = Question(id=uuid4(), question=data.question, author_id=request.user.id)
        session.add(question)
        await session.commit()
        await session.refresh(question)
        return await session.scalar(
            select(Question)
            .where(Question.id == question.id)
            .options(selectinload(Question.author))
            .options(selectinload(Question.ratings))
        )

    @get("/", return_dto=QuestionOverviewDTO, status_code=HTTP_200_OK)
    async def get_questions(self, session: AsyncSession) -> Sequence[Question]:
        """
        :param session: AsyncSession object used to execute the database query and retrieve questions.
        :return: A list of QuestionDTO objects representing the retrieved questions.
        """
        return (
            await session.scalars(
                select(Question).options(selectinload(Question.author)).options(selectinload(Question.ratings))
            )
        ).all()

    @get(path="/{question_id:uuid}", return_dto=QuestionDetailDTO, status_code=HTTP_200_OK)
    async def get_question(self, session: AsyncSession, question_id: UUID) -> Question:
        """
        Retrieves a question by its ID.

        :param session: An `AsyncSession` object representing the database session.
        :param question_id: A `UUID` object representing the ID of the question to retrieve.
        :return: A `QuestionDTO` object containing the retrieved question.
        :raises HTTPException: If the question with the specified ID is not found.
        """

        question = await session.scalar(
            select(Question)
            .where(Question.id == question_id)
            .options(selectinload(Question.author))
            .options(selectinload(Question.ratings).options(selectinload(Rating.user)))
        )

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        return question

    @delete(path="/{question_id:uuid}", status_code=HTTP_204_NO_CONTENT)
    async def delete_question(self, session: AsyncSession, question_id: UUID) -> None:
        """
        Deletes a question from the database.

        :param session: The async session used to interact with the database.
        :param question_id: The UUID of the question to be deleted.
        :return: None

        :raises HTTPException: If the question with the specified ID is not found.
        """

        question = await session.scalar(select(Question).where(Question.id == question_id))

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        await session.delete(question)
        return
