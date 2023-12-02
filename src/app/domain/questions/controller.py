import logging
import math
from uuid import UUID, uuid4

from litestar import Controller, post, get, delete
from litestar.exceptions import HTTPException

from .models import Question
from ..rating.models import IndividualRating
from ..rating.services import RatingService


class QuestionController(Controller):
    path = "/questions/"
    mock_db: dict[UUID, Question] = {}
    rating_service = RatingService()

    async def aggregate_rating(self, question_id: UUID) -> IndividualRating:
        ratings = await self.rating_service.get_ratings(question_id)
        if len(ratings) > 0:
            mean = sum([rating.rating for rating in ratings]) / len(ratings)
            return math.ceil(mean) if mean % 1 >= 0.5 else int(mean)
        else:
            0

    @post("/")
    async def create_question(self, data: Question) -> Question:
        """
        Method to create a new question.

        :param data: The data required to create the question.
        :type data: Question
        :return: The created question.
        :rtype: Question
        """
        question_id = uuid4()
        self.mock_db[question_id] = Question(
            id=question_id, question=data.question, version=data.version, rating=data.rating
        )
        return self.mock_db.get(question_id)

    @get()
    async def list_questions(self) -> list[Question]:
        """
        List Questions

        :return: A list of questions.
        :rtype: list[Question]
        """
        return [
            question.model_copy(update={"rating": await self.aggregate_rating(question.id)})
            for question in self.mock_db.values()
        ]

    @get(path="/{question_id:uuid}")
    async def get_question(self, question_id: UUID) -> Question:
        """
        Get a question by id.

        :param question_id: The UUID of the question to retrieve.
        :return: The Question object corresponding to the given question_id.

        """
        if question_id in self.mock_db:
            return (self.mock_db[question_id]
                    .model_copy(update={"rating": await self.aggregate_rating(question_id)}))
        raise HTTPException(status_code=404, detail="Question not found")


    @delete(path="/{question_id:uuid}")
    async def delete_question(self, question_id: UUID) -> None:
        """
        Delete a question from the database.

        :param question_id: The UUID of the question to be deleted.
        :return: None
        """
        if question_id in self.mock_db:
            self.mock_db.pop(question_id)
        else:
            raise HTTPException(status_code=404, detail="Question not found")
