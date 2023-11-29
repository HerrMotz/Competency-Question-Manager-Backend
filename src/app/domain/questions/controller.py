import logging
from uuid import UUID, uuid4

from litestar import Controller, post, get, delete
from litestar.exceptions import HTTPException

from .models import Question


class QuestionController(Controller):
    path = "/questions/"
    mock_db: dict[UUID, Question] = {}

    @post("/")
    async def create_question(self, data: Question) -> Question:
        question_id = uuid4()
        self.mock_db[question_id] = Question(
            id=question_id, question=data.question, version=data.version, rating=data.rating
        )
        return self.mock_db.get(question_id)

    @get()
    async def list_questions(self) -> list[Question]:
        return list(self.mock_db.values())

    @get(path="/{question_id:uuid}")
    async def get_question(self, question_id: UUID) -> Question:
        if question_id in self.mock_db:
            return self.mock_db[question_id]
        raise HTTPException(status_code=404, detail="Question not found")

    @delete(path="/{question_id:uuid}")
    async def delete_question(self, question_id: UUID) -> None:
        if question_id in self.mock_db:
            self.mock_db.pop(question_id)
        else:
            raise HTTPException(status_code=404, detail="Question not found")
