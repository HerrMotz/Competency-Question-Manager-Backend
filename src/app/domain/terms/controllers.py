from typing import Sequence
from uuid import UUID

from domain.questions.dtos import QuestionOverviewDTO
from domain.questions.models import Question
from litestar import Controller, delete, get, put
from sqlalchemy.ext.asyncio import AsyncSession

from .dtos import PassageDTO, TermDTO
from .models import Passage, Term


class TermController(Controller):
    path = "/terms"

    @get("/", return_dto=TermDTO)
    def get_all(self, session: AsyncSession) -> Sequence[Term]:
        """Gets all `Terms` with in the system."""
        ...

    @get("/{project_id:uuid}", return_dto=TermDTO)
    def get_all_project(self, session: AsyncSession, project_id: UUID) -> Sequence[Term]:
        """Gets all `Passage`s and `Term`s within a `Project`."""
        ...

    @get("/{question_id:uuid}", return_dto=TermDTO)
    def get_all_question_project(self, session: AsyncSession, question_id: UUID) -> Sequence[Term]:
        """Gets all `Passage`s and `Term`s associated with a `Question`."""
        ...

    @put("/{question_id:uuid}", return_dto=TermDTO)
    def add(self, session: AsyncSession, question_id: UUID) -> Sequence[Term]:
        """Adds one or more `Passage`s and `Term`s to a `Question` or updates existing `Passage`s."""
        ...

    @delete("/{question_id:uuid}", return_dto=TermDTO)
    def delete(self, session: AsyncSession, question_id: UUID) -> Sequence[Term]:
        """Removes one or more `Passage`s and `Term`s from a `Question`."""
        ...

    @get("/{project_id:uuid}/{question_id:uuid}", return_dto=PassageDTO)
    def get_from_question(self, session: AsyncSession, project_id: UUID, question_id: UUID) -> Sequence[PassageDTO]:
        """Gets all `Passage`s marked within a given `Question`."""
        ...

    @get("/{project_id:uuid}/{term_id:uuid}/questions", return_dto=QuestionOverviewDTO)
    def get_from_term(self, session: AsyncSession, project_id: UUID, term_id: UUID) -> Sequence[QuestionOverviewDTO]:
        """Gets all `Question`s within a given `Project` that share the given `Term`."""
        ...
