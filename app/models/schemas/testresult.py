from pydantic import BaseModel


class TestResult(BaseModel):
    test_id: int
    student_id: str
    class_id: int
    score: int
    answers: list[str]