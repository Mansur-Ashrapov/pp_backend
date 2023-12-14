from pydantic import BaseModel

from app.db.exceptions import EntityDoesNotExist
from app.db.tables import Class as ClassModel
from app.db.repositories.base import BaseRepository
from app.models.schemas.classroom import Class, ClassIn

class ClassRepository(BaseRepository):
    async def get_class_by_id(self, id: int) -> Class:
        class_data = await self.database.fetch_one(ClassModel.select().where(ClassModel.c.id == id))
        if class_data:
            return Class(id=class_data.id, name=class_data.name, teacher_id=class_data.teacher_id)
        raise EntityDoesNotExist(f"Class with id {id} does not exist")
    
    async def delete(self, id: int) -> None:
        await self.database.execute(ClassModel.delete().where(ClassModel.c.id == id))
    
    async def update(self, id: int, class_data: BaseModel) -> None:
        await self.database.execute(ClassModel.update().where(ClassModel.c.id == id).values(**class_data.dict()))

    async def get_classes_by_teacher_id(self, teacher_id: str) -> list[Class]:
        classes = await self.database.fetch_all(ClassModel.c.teacher_id == teacher_id)
        return [Class(id=class_data.id, name=class_data.name, teacher_id=class_data.teacher_id) for class_data in classes]

    async def create_class(self, class_data: ClassIn) -> None:
        await self.database.execute(ClassModel.insert().values(**class_data.dict()))
    