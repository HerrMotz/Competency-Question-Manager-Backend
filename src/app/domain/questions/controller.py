from typing import Annotated, Any, Sequence, TypeVar
from uuid import UUID
from domain.consolidations.models import Consolidation
from domain.groups.models import Group
from litestar import Controller, Request, delete, get, post
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException
from litestar.params import Body
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..accounts.models import User
from .dtos import QuestionCreate, QuestionCreateDTO, QuestionDetailDTO, QuestionOverviewDTO
from .models import Question

T = TypeVar("T")
JsonEncoded = Annotated[T, Body(media_type=RequestEncodingType.JSON)]


class QuestionController(Controller):
    path = "/questions/"
    tags = ["Questions"]

    default_options = [selectinload(Question.author), selectinload(Question.ratings)]
    detail_options = [
        selectinload(Question.author),
        selectinload(Question.ratings),
        selectinload(Question.consolidations).options(selectinload(Consolidation.questions)),
        selectinload(Question.group).options(selectinload(Group.project)),
    ]

    @post("/{group_id:uuid}", dto=QuestionCreateDTO, return_dto=QuestionDetailDTO, status_code=HTTP_201_CREATED)
    async def create_question(
        self,
        session: AsyncSession,
        data: JsonEncoded[QuestionCreate],
        request: Request[User, Any, Any],
        group_id: UUID,
    ) -> Question:
        """
        Creates a new `Question`

        :param request: Request[User, Any, Any]
        :param session: The session object to use for database operations.
        :param data: The question data to be created.
        :return: The created question data.
        """
        try:
            question = Question(question=data.question, author_id=request.user.id, group_id=group_id)
            session.add(question)
            await session.commit()
            await session.refresh(question)
            question = await session.scalar(
                select(Question).where(Question.id == question.id).options(*self.detail_options)
            )
            if question:
                return question
            else:
                raise HTTPException(status_code=404, detail="Question not found.")
        except IntegrityError:
            raise HTTPException(status_code=400, detail="Integrity violated.")

    @get("/", return_dto=QuestionOverviewDTO, status_code=HTTP_200_OK)
    async def get_questions(self, session: AsyncSession) -> Sequence[Question]:
        """
        :param session: AsyncSession object used to execute the database query and retrieve questions.
        :return: A list of QuestionDTO objects representing the retrieved questions.
        """
        return (await session.scalars(select(Question).options(*self.default_options))).all()

    @get("/{group_id:uuid}", return_dto=QuestionOverviewDTO, status_code=HTTP_200_OK)
    async def get_group_questions(self, session: AsyncSession, group_id: UUID) -> Sequence[Question]:
        """Gets all `Question`s belonging to a given `Group`."""
        return (
            await session.scalars(select(Question).where(Question.group_id == group_id).options(*self.default_options))
        ).all()

    @get("/{group_id:uuid}/{question_id:uuid}", return_dto=QuestionDetailDTO, status_code=HTTP_200_OK)
    async def get_question(self, session: AsyncSession, question_id: UUID, group_id: UUID) -> Question:
        """
        Retrieves a question by its ID.

        :param session: An `AsyncSession` object representing the database session.
        :param question_id: A `UUID` object representing the ID of the question to retrieve.
        :return: A `QuestionDTO` object containing the retrieved question.
        :raises HTTPException: If the question with the specified ID is not found.
        """

        question = await session.scalar(
            select(Question)
            .where(Question.id == question_id, Question.group_id == group_id)
            .options(*self.detail_options)
        )

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        return question

    @delete("/{group_id:uuid}/{question_id:uuid}", status_code=HTTP_204_NO_CONTENT)
    async def delete_question(self, session: AsyncSession, question_id: UUID, group_id: UUID) -> None:
        """
        Deletes a question from the database.

        :param session: The async session used to interact with the database.
        :param question_id: The UUID of the question to be deleted.
        :return: None

        :raises HTTPException: If the question with the specified ID is not found.
        """

        question = await session.scalar(
            select(Question).where(Question.id == question_id, Question.group_id == group_id)
        )

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        await session.delete(question)
        return
