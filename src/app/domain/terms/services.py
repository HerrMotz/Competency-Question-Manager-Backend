from typing import Iterable, Sequence
from uuid import UUID

from domain.questions.models import Question
from litestar.exceptions import NotFoundException
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.base import ExecutableOption
from sqlalchemy.sql.elements import ColumnElement

from .dtos import AnnotationAddDTO, AnnotationRemove
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

    @staticmethod
    async def list_questions_by_term(
        session: AsyncSession,
        term_id: UUID,
        project_id: UUID,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Sequence[Question]:
        options = [] if not options else options
        subquery = select(Term).where(Term.id == term_id, Term.project_id == project_id).subquery()
        statement = select(Question).join(Passage, Question.annotations)
        statement = statement.join(subquery, Passage.term_id == subquery.c.id)
        statement = statement.options(*options)
        scalars = await session.scalars(statement)
        return scalars.all()

    @staticmethod
    async def get_or_create_term(session: AsyncSession, project_id: UUID, term: str) -> Term:
        if model := await session.scalar(select(Term).where(Term.content == term, Term.project_id == project_id)):
            return model

        model = Term(content=term, project_id=project_id)
        session.add(model)
        await session.commit()
        await session.refresh(model)
        return model

    @staticmethod
    async def get_or_create_passage(
        session: AsyncSession,
        term_id: UUID,
        passage: str,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Passage:
        options = [] if not options else options
        if model := await session.scalar(select(Passage).where(Passage.content == passage, Passage.term_id == term_id)):
            return model

        model = Passage(content=passage, term_id=term_id)
        session.add(model)
        await session.commit()
        await session.refresh(model)
        return model # await session.scalar(select(Passage).where(Passage.id == model.id).options(*options))  # pyright: ignore

    @staticmethod
    async def annotate(
        session: AsyncSession,
        question_id: UUID,
        data: AnnotationAddDTO,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Sequence[Passage]:
        options = [] if not options else options
        statement = (
            select(Question)
            .where(Question.id == question_id)
            .options(
                selectinload(Question.annotations).options(selectinload(Passage.term)),
                selectinload(Question.group),
                *options,
            )
        )
        if question := await session.scalar(statement):
            for annotation in data.annotations:
                term = await AnnotationService.get_or_create_term(session, question.group.project_id, annotation.term)
                passage = await AnnotationService.get_or_create_passage(session, term.id, annotation.passage)
                question = await session.scalar(statement)
                assert question
                if passage not in question.annotations:
                    question.annotations.append(passage)
            return question.annotations
        raise NotFoundException()

    @staticmethod
    async def remove_annotations(
        session: AsyncSession,
        question_id: UUID,
        data: AnnotationRemove,
        options: Iterable[ExecutableOption] | None = None,
    ) -> Sequence[Passage]:
        options = [] if not options else options
        statement = (
            select(Question)
            .where(Question.id == question_id)
            .options(selectinload(Question.annotations), selectinload(Question.group))
        )
        if question := await session.scalar(statement):
            if data.term_ids:
                statement = select(Passage).where(
                    Passage.term_id.in_(data.term_ids),
                    Passage.questions.any(Question.id == question_id),
                )
                scalars = (await session.scalars(statement)).all()
                _ = [question.annotations.remove(scalar) for scalar in scalars]
                await session.commit()

            if data.passage_ids:
                statement = select(Passage).where(
                    Passage.id.in_(data.passage_ids),
                    Passage.questions.any(Question.id == question_id),
                )
                scalars = (await session.scalars(statement)).all()
                _ = [question.annotations.remove(scalar) for scalar in scalars]
                await session.commit()

            scalars = await session.scalars(select(Passage).where(Passage.questions.any(Question.id == question_id)))
            return scalars.all()
        raise NotFoundException()
