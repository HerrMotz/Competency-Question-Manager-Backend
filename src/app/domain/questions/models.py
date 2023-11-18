from pydantic import BaseModel


class Question(BaseModel):
    id: str
    question: str
    version: int