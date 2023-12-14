from app.db.exceptions import EntityDoesNotExist
from app.db.tables import TestResult as TestResultModel
from app.db.repositories.base import BaseRepository
from app.models.schemas.testresult import TestResult


class TestResultRepository(BaseRepository):
    async def get_test_by_id(self, id: int) -> TestResult:
        test_result = await self.database.fetch_one(TestResultModel.select().where(TestResultModel.c.id == id))
        if test_result:
            return TestResult(
                        test_id=test_result.test_id, 
                        answers=test_result.answers, 
                        student_id=test_result.student_id, 
                        class_id=test_result.class_id, 
                        score=test_result.score
                    )
        raise EntityDoesNotExist(f"Result for test with id {id} does not exist")

    async def get_test_by_class_id(self, class_id: int) -> list[TestResult]:
        tests = await self.database.fetch_all(TestResultModel.c.class_id == class_id)
        return [TestResult(
                    test_id=test_result.test_id, 
                    answers=test_result.answers, 
                    student_id=test_result.student_id, 
                    class_id=test_result.class_id, 
                    score=test_result.score
                ) for test_result in tests]
    
    async def get_test_by_student_id(self, student_id: str) -> list[TestResult]:
        tests = await self.database.fetch_all(TestResultModel.c.student_id == student_id)
        return [TestResult(
                    test_id=test_result.test_id, 
                    answers=test_result.answers, 
                    student_id=test_result.student_id,
                    class_id=test_result.class_id, 
                    score=test_result.score
                ) for test_result in tests]
    
    async def create_test(self, test_data: TestResult) -> None:
        await self.database.execute(TestResultModel.insert().values(**test_data.dict()))
    