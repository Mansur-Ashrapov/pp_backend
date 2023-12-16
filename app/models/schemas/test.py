from pydantic import BaseModel


class Test(BaseModel):
    id: int
    name: str
    answers: list[str]
    teacher_id: int

class TestIn(BaseModel):
    name: str
    answers: list[str]
    
class TestUpdate(BaseModel):
    id: int
    name: str
    answers: list[str]