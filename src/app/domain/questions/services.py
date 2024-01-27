from typing import Iterable, Sequence
from uuid import UUID

from domain.groups.models import Group
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.base import ExecutableOption

from .models import Question


class QuestionService:
    @staticmethod
    async def get_questions_by_project(
        session: AsyncSession,
        project_id: UUID,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Sequence[Question]:
        options = [] if not options else options
        statement = select(Question).join(Group).filter(Group.project_id == project_id).options(*options)
        return (await session.scalars(statement)).all()
