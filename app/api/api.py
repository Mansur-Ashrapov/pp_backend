from fastapi.routing import APIRouter

from app.api.routes import auth, student, teacher_class, test, testresult

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["authentication"])
router.include_router(teacher_class.router, prefix="/class", tags=["teacher class"])
router.include_router(student.router, prefix="/student", tags=["student"])
router.include_router(test.router, prefix="/test", tags=["test"])
router.include_router(testresult.router, prefix="/testresult", tags=["test result"])
