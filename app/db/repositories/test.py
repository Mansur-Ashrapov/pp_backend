from pydantic import BaseModel

from app.db.exceptions import EntityDoesNotExist
from app.db.tables import Test as TestModel
from app.db.repositories.base import BaseRepository
from app.models.schemas.test import TestIn, Test

class TestRepository(BaseRepository):
    async def get_test_by_id(self, id: int) -> Test:
        test = await self.database.fetch_one(TestModel.select().where(TestModel.c.id == id))
        if test:
            return Test(id=test.id, name=test.name, answers=test.answers, teacher_id=test.teacher_id)
        raise EntityDoesNotExist(f"Test with id {id} does not exist")

    async def get_test_by_teacher_id(self, teacher_id: int) -> list[Test]:
        tests = await self.database.fetch_all(TestModel.c.teacher_id == teacher_id)
        return [Test(id=test.id, name=test.name, answers=test.answers, teacher_id=test.teacher_id) for test in tests]

    async def delete(self, id: int) -> None:
        await self.database.execute(TestModel.delete().where(TestModel.c.id == id))
    
    async def update(self, id: int, test: BaseModel) -> None:
        await self.database.execute(TestModel.update().where(TestModel.c.id == id).values(**test.dict()))

    async def create_test(self, test_data: TestIn) -> None:
        await self.database.execute(TestModel.insert().values(
            name=test_data.name,
            answers=test_data.answers,
            teacher_id=test_data.teacher_id
        ))
    