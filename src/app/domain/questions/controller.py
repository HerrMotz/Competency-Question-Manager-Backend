from litestar import Controller, post, get, delete
from litestar.exceptions import HTTPException

from .models import Question


class QuestionController(Controller):
    path = "/questions/"
    mock_db: dict[str, Question] = {}

    @post()
    async def create_question(self, data: Question) -> Question:
        self.mock_db[data.id] = data
        return self.mock_db.get(data.id)

    @get()
    async def list_questions(self) -> list[Question]:
        return list(self.mock_db.values())

    @get(path="/{question_id:str}")
    async def get_user(self, question_id: str) -> Question:
        if question_id in self.mock_db:
            return self.mock_db[question_id]
        raise HTTPException(status_code=404, detail="Question not found")

    @delete(path="/{question_id:str}")
    async def delete_user(self, question_id: str) -> None:
        if question_id in self.mock_db:
            self.mock_db.pop(question_id)
        else:
            raise HTTPException(status_code=404, detail="Question not found")
