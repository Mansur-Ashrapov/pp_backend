import asyncio

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status
from asyncpg.exceptions import UndefinedObjectError, UniqueViolationError, ForeignKeyViolationError

from app.db.exceptions import EntityDoesNotExist
from app.api.dependecies.database import get_repository
from app.api.dependecies.auth import get_oauth2

from app.models.schemas.test import Test, TestIn, TestUpdate

from app.db.repositories.test import TestRepository
from app.db.repositories.users import UserRepository

from app.services.security import get_user_from_payload


router = APIRouter()


@router.post('/')
async def create_test(
        test: TestIn,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        test_repo: TestRepository = Depends(get_repository(TestRepository))
    ):
    """Создать тест"""
    try:
        user = await get_user_from_payload(token, users_repo)
        await test_repo.create_test(test, user.id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    return {'status_code': status.HTTP_201_CREATED}


@router.put('/')
async def change_test(
        test: TestUpdate,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        test_repo: TestRepository = Depends(get_repository(TestRepository))
    ):
    """Изменить тест"""
    try:
        await get_user_from_payload(token, users_repo)
        await test_repo.update(test.id, test)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except EntityDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])
    except UndefinedObjectError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Такого теста не существует")
    return {'status_code': status.HTTP_201_CREATED}

        
@router.get('/{test_id}', response_model=Test)
async def get_test_by_id(
        test_id: int,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        test_repo: TestRepository = Depends(get_repository(TestRepository))
    ):
    """Получить данные о тесте"""
    try:
        await get_user_from_payload(token, users_repo)
        test = await test_repo.get_test_by_id(test_id)
        return test
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except EntityDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])
            
@router.delete('/{test_id}')
async def delete(
        test_id: int,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        test_repo: TestRepository = Depends(get_repository(TestRepository))
    ):
    """Удалить тест"""
    try:
        await get_user_from_payload(token, users_repo)
        await test_repo.delete(test_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except EntityDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.get('/', response_model=list[Test])
async def get_tests_by_teacher_id(
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        test_repo: TestRepository = Depends(get_repository(TestRepository))
    ):
    """Получить тесты принадлежащие учителю"""
    try:
        user = await get_user_from_payload(token, users_repo)
        tests = await test_repo.get_test_by_teacher_id(user.id)
        return tests
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    