import asyncio

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from asyncpg.exceptions import UniqueViolationError

from app.db.exceptions import EntityDoesNotExist
from app.api.dependecies.database import get_repository
from app.api.dependecies.auth import get_oauth2

from app.models.schemas.auth import Token
from app.models.schemas.student import Student, StudentIn
from app.models.schemas.test import Test, TestIn
from app.models.schemas.testresult import TestResult
from app.models.schemas.classroom import Class, ClassIn, ClassOut
from app.models.schemas.users import User

from app.db.repositories.classroom import ClassRepository
from app.db.repositories.student import StudentRepository
from app.db.repositories.test import TestRepository
from app.db.repositories.testresult import TestResultRepository
from app.db.repositories.users import UserRepository

from app.services.security import get_password_hash, get_user_from_payload


router = APIRouter()


@router.get('/', response_model=list[ClassOut])
async def get_classes(
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        class_repo: ClassRepository = Depends(get_repository(ClassRepository)),
        students_repo: StudentRepository = Depends(get_repository(StudentRepository))
    ):
    try:
        user = await get_user_from_payload(token, users_repo)
        classes = await class_repo.get_classes_by_teacher_id(user.id)
        out = await asyncio.gather(*[ClassOut(**class_data.dict(),
                                              students=students_repo.get_students_by_class_id(class_data.id))
                                              for class_data in classes])
        return out
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
        
@router.post('/')
async def create_class(
        class_data: ClassIn,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        class_repo: ClassRepository = Depends(get_repository(ClassRepository))
    ):
    try:
        await get_user_from_payload(token, users_repo)
        await class_repo.create_class(class_data)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)