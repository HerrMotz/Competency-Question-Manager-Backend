from typing import Sequence
from uuid import UUID

from domain.questions.dtos import QuestionOverviewDTO
from domain.questions.models import Question
from litestar import Controller, get, put
from sqlalchemy.ext.asyncio import AsyncSession

from .dtos import AnnotationAddDTO, AnnotationRemove, AnnotationRemoveDTO, PassageDTO, TermDTO
from .models import Passage, Term
from .services import AnnotationService

from domain.questions.controller import QuestionController


class TermController(Controller):
    tags = ["Terms"]
    path = "/terms"

    @get("/", summary="Get All", return_dto=TermDTO)
    async def get_all(self, session: AsyncSession) -> Sequence[Term]:
        """Gets all `Terms` within the system."""
        return await AnnotationService.list(session)

    @get("/project/{project_id:uuid}", summary="Get Terms by Project", return_dto=TermDTO)
    async def get_all_project(self, session: AsyncSession, project_id: UUID) -> Sequence[Term]:
        """Gets all `Term`s and  `Passage`s within a `Project`."""
        return await AnnotationService.list(session, (Term.project_id == project_id,))

    @get("/question/{question_id:uuid}", summary="Get Passages by Question", return_dto=PassageDTO)
    async def get_all_question_project(self, session: AsyncSession, question_id: UUID) -> Sequence[Passage]:
        """Gets all `Passage`s associated with a `Question`."""
        return await AnnotationService.list_by_question(session, question_id)

    @put("/add/{question_id:uuid}", summary="Add Annotations to Question", return_dto=PassageDTO)
    async def add(self, session: AsyncSession, question_id: UUID, data: AnnotationAddDTO) -> Sequence[Passage]:
        """Adds one or more `Passage`s and `Term`s to a `Question` or updates existing `Passage`s."""
        return await AnnotationService.annotate(session, question_id, data)

    @put("/remove/{question_id:uuid}", summary="Remove Annotations from Question", dto=AnnotationRemoveDTO, return_dto=PassageDTO)
    async def delete(self, session: AsyncSession, question_id: UUID, data: AnnotationRemove) -> Sequence[Passage]:
        """Removes one or more `Passage`s and `Term`s from a `Question`, returns leftover `Passage`s."""
        return await AnnotationService.remove_annotations(session, question_id, data)

    @get("/{project_id:uuid}/{term_id:uuid}", summary="Get Question by Term", return_dto=QuestionOverviewDTO)
    async def get_by_term(self, session: AsyncSession, project_id: UUID, term_id: UUID) -> Sequence[Question]:
        """Gets all `Question`s within a given `Project` that share the given `Term`."""
        return await AnnotationService.list_questions_by_term(
            session, term_id, project_id, QuestionController.default_options
        )
