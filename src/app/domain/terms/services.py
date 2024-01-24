from typing import Iterable, Sequence
from uuid import UUID

from domain.questions.models import Question
from litestar.exceptions import NotFoundException
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.elements import ColumnElement

from .models import Passage, Term


class AnnotationService:
    @staticmethod
    async def list(
        session: AsyncSession,
        filters: Iterable[ColumnElement[bool]] | None = None,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Sequence[Term]:
        options = [] if not options else options
        filters = [] if not filters else filters
        statement = select(Term).where(*filters).options(*options)
        scalars = await session.scalars(statement)
        return scalars.all()

    @staticmethod
    async def list_by_question(
        session: AsyncSession,
        question_id: UUID,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Sequence[Passage]:
        options = [] if not options else options
        statement = select(Question).where(Question.id == question_id)
        if not await session.scalar(statement):
            raise NotFoundException()

        statement = select(Passage).where(Passage.questions.any(Question.id == question_id)).options(*options)
        scalars = await session.scalars(statement)
        return scalars.all()
