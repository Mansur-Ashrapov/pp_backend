from pydantic import BaseModel

from app.db.exceptions import EntityDoesNotExist
from app.db.tables import Student as StudentModel
from app.db.repositories.base import BaseRepository
from app.models.schemas.student import Student, StudentIn
from app.db.utils import create_id_len_five


class StudentRepository(BaseRepository):
    async def get_student_by_id(self, id: str) -> Student:
        student = await self.database.fetch_one(StudentModel.select().where(StudentModel.c.id == id))
        if student:
            return Student(id=student.id, fullname=student.fullname, class_id=student.class_id)
        raise EntityDoesNotExist(f"Student with id {id} does not exist")

    async def get_students_by_class_id(self, class_id: int) -> list[Student]:
        students = await self.database.fetch_all(StudentModel.c.class_id == class_id)
        return [Student(id=student.id, fullname=student.fullname, class_id=student.class_id) for student in students]

    async def delete(self, id: str) -> None:
        await self.database.execute(StudentModel.delete().where(StudentModel.c.id == id))

    async def update(self, id: str, student: BaseModel):
        await self.database.execute(StudentModel.update().where(StudentModel.c.id == id).values(**student.dict()))

    async def create_student(self, student_data: StudentIn) -> None:
        while True:
            student_id = create_id_len_five()
            try: 
                await self.get_student_by_id(student_id)
                continue
            except EntityDoesNotExist:
                break
        
        await self.database.execute(StudentModel.insert().values(
            id=student_id,
            fullname=student_data.fullname,
            class_id=student_data.class_id
        ))
    