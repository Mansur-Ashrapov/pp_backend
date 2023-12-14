import asyncio

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from asyncpg.exceptions import UniqueViolationError, ForeignKeyViolationError

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


@router.post('/')
async def create_student(
        student: StudentIn,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        students_repo: StudentRepository = Depends(get_repository(StudentRepository))
    ):
    try:
        await get_user_from_payload(token, users_repo)
        await students_repo.create_student(student)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except ForeignKeyViolationError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Class with id {student.class_id} not found")
    return {'status_code': status.HTTP_201_CREATED}

        
@router.get('/', response_model=Student)
async def get_student(
        student_id: str,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        students_repo: StudentRepository = Depends(get_repository(StudentRepository))
    ):
    try:
        await get_user_from_payload(token, users_repo)
        student = await students_repo.get_student_by_id(student_id)
        return student
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)