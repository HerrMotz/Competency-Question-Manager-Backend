from uuid import UUID

from litestar import Controller, post, get, delete
from litestar.exceptions import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Question, QuestionDTO


class QuestionController(Controller):
    path = "/questions/"
    mock_db: dict[UUID, Question] = {}

    @post("/")
    async def create_question(self, session: AsyncSession, data: QuestionDTO) -> QuestionDTO:
        """
        Creates a question in the session.

        :param session: The session object to use for database operations.
        :param data: The question data to be created.
        :return: The created question data.
        """
        question = Question(question=data.question, version=data.version)
        session.add(question)
        await session.commit()
        return data

    @get("/")
    async def get_questions(self, session: AsyncSession) -> list[QuestionDTO]:
        """
        :param session: AsyncSession object used to execute the database query and retrieve questions.
        :return: A list of QuestionDTO objects representing the retrieved questions.
        """
        questions = await session.execute(select(Question))
        return [QuestionDTO.model_validate(question) for question in questions.scalars()]

    @get(path="/{question_id:uuid}")
    async def get_question(self, session: AsyncSession, question_id: UUID) -> QuestionDTO:
        """
        Retrieves a question by its ID.

        :param session: An `AsyncSession` object representing the database session.
        :param question_id: A `UUID` object representing the ID of the question to retrieve.
        :return: A `QuestionDTO` object containing the retrieved question.
        :raises HTTPException: If the question with the specified ID is not found.
        """
        question = await session.execute(select(Question).where(Question.id == question_id))
        if not question.scalar():
            raise HTTPException(status_code=404, detail="Question not found")
        return QuestionDTO.model_validate(question.scalar())

    @delete(path="/{question_id:uuid}")
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
