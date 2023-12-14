from pydantic import BaseModel

from app.models.schemas.student import Student

class Class(BaseModel):
    id: int
    name: str
    teacher_id: str

class ClassIn(BaseModel):
    name: str
    teacher_id: str

class ClassOut(Class):
    students: list[Student]
