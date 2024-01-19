from typing import Iterable, Sequence
from uuid import UUID

from domain.questions.models import Question
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from .dtos import ConsolidationCreate, ConsolidationUpdate, MoveQuestion
from .models import Consolidation


class ConsolidationService:
    @staticmethod
    async def get_consolidation(
        session: AsyncSession,
        id: UUID,
        project_id: UUID | None = None,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Consolidation:
        """Gets a single `Consolidation`.

        :param session: An active database session.
        :param id: Id of the `Consolidation`.
        :param project_id: Id of the `Consolidation`s `Project`..
        :param options: Additional loading options, defaults to None.
        :raises HTTPException: If no `Consolidation` was found.
        :return: A `Consolidation`.
        """
        if project_id:
            statement = select(Consolidation).where(Consolidation.id == id, Consolidation.project_id == project_id)
        else:
            statement = select(Consolidation).where(Consolidation.id == id)

        if options:
            statement = statement.options(*options)

        if consolidation := await session.scalar(statement):
            return consolidation
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    @staticmethod
    async def get_consolidations(
        session: AsyncSession,
        project_id: UUID | None = None,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Sequence[Consolidation]:
        """Gets a all `Consolidations`.

        :param session: An active database session.
        :param options: Additional loading options, defaults to None.
        :return: A sequence of all `Consolidations`.
        """
        if project_id:
            statement = select(Consolidation).where(Consolidation.project_id == project_id)
        else:
            statement = select(Consolidation)

        if options:
            statement = statement.options(*options)
        return (await session.scalars(statement)).all()

    @staticmethod
    async def create_consolidation(
        session: AsyncSession,
        user_id: UUID,
        data: ConsolidationCreate,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Consolidation:
        """Creates a new `Consolidation`.

        :param session: An active database session.
        :param user_id: The authors id.
        :param data: Contents of the `Consolidation`.
        :param options: Additional loading options, defaults to None.
        :raises HTTPException: If database integrity was violated.
        :return: The created `Consolidation`.
        """
        questions: Sequence[Question] = []
        if data.ids:
            questions_ = await session.scalars(select(Question).where(Question.id.in_(data.ids)))
            questions = questions_.all()

        try:
            consolidation = Consolidation(name=data.name, questions=questions, engineer_id=user_id)
            session.add(consolidation)
            await session.commit()
        except IntegrityError as error:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST) from error

        await session.refresh(consolidation)
        return await ConsolidationService.get_consolidation(session, consolidation.id, options=options)

    @staticmethod
    async def delete_consolidation(session: AsyncSession, id: UUID) -> bool:
        """Deletes an existing `Consolidation`.

        :param session: An active database session.
        :param id: Id of the `Consolidation`.
        :return: `True` if successfully deleted.
        """
        consolidation = await ConsolidationService.get_consolidation(session, id)
        await session.delete(consolidation)
        return True

    @staticmethod
    async def update_consolidation(
        session: AsyncSession,
        id: UUID,
        data: ConsolidationUpdate,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Consolidation:
        """Updates an existing `Consolidation`.

        :param session: An active database session.
        :param id: Id of the `Consolidation`.
        :param data: Contents of the `Consolidation`.
        :param options: Additional loading options, defaults to None.
        :raises HTTPException: If database integrity was violated.
        :raises HTTPException: If no `Consolidation` was found.
        :return: The updated `Consolidation`.
        """
        if data.name:
            consolidation = await ConsolidationService.get_consolidation(session, id, options=options)
            consolidation.name = data.name
            try:
                await session.commit()
            except IntegrityError as error:
                raise HTTPException(status_code=HTTP_400_BAD_REQUEST) from error
            return consolidation
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    @staticmethod
    async def add_questions(
        session: AsyncSession,
        id: UUID,
        data: MoveQuestion,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Consolidation:
        """Add `Questions` to an existing `Consolidation`.

        :param session: An active database session.
        :param id: Id of the `Consolidation`.
        :param data: A list of `Question` ids.
        :param options: Additional loading options, defaults to None.
        :raises HTTPException: If no `Consolidation` was found.
        :return: The updated `Consolidation`.
        """
        if not data.ids:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST)

        consolidation = await ConsolidationService.get_consolidation(session, id, options=options)
        questions = await session.scalars(select(Question).where(Question.id.in_(data.ids)))
        consolidation.questions.extend(questions)
        return consolidation

    @staticmethod
    async def remove_questions(
        session: AsyncSession,
        id: UUID,
        data: MoveQuestion,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Consolidation:
        """Removes `Questions` from an existing `Consolidation`.

        :param session: An active database session.
        :param id: Id of the `Consolidation`.
        :param data: A list of `Question` ids.
        :param options: Additional loading options, defaults to None.
        :raises HTTPException: If no `Consolidation` was found.
        :return: The updated `Consolidation`.
        """
        if not data.ids:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST)

        consolidation = await ConsolidationService.get_consolidation(session, id, options=options)
        questions = await session.scalars(select(Question).where(Question.id.in_(data.ids)))
        _ = [consolidation.questions.remove(question) for question in questions]
        return consolidation
