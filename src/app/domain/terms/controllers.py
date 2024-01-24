from typing import Sequence
from uuid import UUID

from domain.questions.dtos import QuestionOverviewDTO
from domain.questions.models import Question
from litestar import Controller, delete, get, put
from sqlalchemy.ext.asyncio import AsyncSession

from .dtos import AnnotationAddDTO, AnnotationRemove, AnnotationRemoveDTO, PassageDTO, TermDTO
from .models import Passage, Term
from .services import AnnotationService


class TermController(Controller):
    path = "/terms"

    @get("/", return_dto=TermDTO)
    async def get_all(self, session: AsyncSession) -> Sequence[Term]:
        """Gets all `Terms` within the system."""
        return await AnnotationService.list(session)

    @get("/{project_id:uuid}", return_dto=TermDTO)
    async def get_all_project(self, session: AsyncSession, project_id: UUID) -> Sequence[Term]:
        """Gets all `Term`s and  `Passage`s within a `Project`."""
        return await AnnotationService.list(session, (Term.project_id == project_id,))

    @get("/{question_id:uuid}", return_dto=PassageDTO)
    async def get_all_question_project(self, session: AsyncSession, question_id: UUID) -> Sequence[Passage]:
        """Gets all `Passage`s associated with a `Question`."""
        return await AnnotationService.list_by_question(session, question_id)

    @put("/{question_id:uuid}", return_dto=PassageDTO)
    async def add(self, session: AsyncSession, question_id: UUID, data: AnnotationAddDTO) -> Sequence[Passage]:
        """Adds one or more `Passage`s and `Term`s to a `Question` or updates existing `Passage`s."""
        return await AnnotationService.annotate(session, question_id, data)

    @delete("/{question_id:uuid}", dto=AnnotationRemoveDTO, return_dto=PassageDTO)
    async def delete(self, session: AsyncSession, question_id: UUID, data: AnnotationRemove) -> Sequence[Passage]:
        """Removes one or more `Passage`s and `Term`s from a `Question`, returns leftover `Passage`s."""
        return await AnnotationService.remove_annotations(session, question_id, data)

    @get("/{project_id:uuid}/{term_id:uuid}/questions", return_dto=QuestionOverviewDTO)
    async def get_by_term(self, session: AsyncSession, project_id: UUID, term_id: UUID) -> Sequence[Question]:
        """Gets all `Question`s within a given `Project` that share the given `Term`."""
        return await AnnotationService.list_questions_by_term(session, term_id, project_id)
