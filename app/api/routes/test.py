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
async def create_test(
        test: TestIn,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        test_repo: TestRepository = Depends(get_repository(TestRepository))
    ):
    try:
        await get_user_from_payload(token, users_repo)
        await test_repo.create_test(test)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return {'status_code': status.HTTP_201_CREATED}

        
@router.get('/{test_id}', response_model=Test)
async def get_test_by_id(
        test_id: str,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        test_repo: TestRepository = Depends(get_repository(TestRepository))
    ):
    try:
        await get_user_from_payload(token, users_repo)
        test = await test_repo.get_test_by_id(test_id)
        return test
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
@router.get('/', response_model=list[Test])
async def get_tests_by_teacher_id(
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        test_repo: TestRepository = Depends(get_repository(TestRepository))
    ):
    try:
        user = await get_user_from_payload(token, users_repo)
        tests = await test_repo.get_test_by_teacher_id(user.id)
        return tests
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    