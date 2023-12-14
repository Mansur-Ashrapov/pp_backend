from pydantic import BaseModel


class Student(BaseModel):
    id: str
    fullname: str
    class_id: int

class StudentIn(BaseModel):
    fullname: str
    class_id: int
