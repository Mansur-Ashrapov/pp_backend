import asyncio

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from app.db.exceptions import EntityDoesNotExist
from app.api.dependecies.database import get_repository
from app.api.dependecies.auth import get_oauth2

from app.models.schemas.classroom import ClassIn, ClassOut, ClassUpdate

from app.db.repositories.classroom import ClassRepository
from app.db.repositories.student import StudentRepository
from app.db.repositories.users import UserRepository

from app.services.security import get_user_from_payload


router = APIRouter()


@router.get('/', response_model=list[ClassOut])
async def get_classes(
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        class_repo: ClassRepository = Depends(get_repository(ClassRepository)),
        students_repo: StudentRepository = Depends(get_repository(StudentRepository))
    ):
    """Получить все классы преподавателя и учеников этих классов"""
    try:
        user = await get_user_from_payload(token, users_repo)
        classes = await class_repo.get_classes_by_teacher_id(user.id)
        out = await asyncio.gather(*[students_repo.get_students_by_class_id(class_data.id) for class_data in classes])
        return [ClassOut(**class_data.dict(), students=students) for students, class_data in zip(out, classes)]
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except EntityDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])

@router.get('/{class_id}', response_model=ClassOut)
async def get_classes(
        class_id: int,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        class_repo: ClassRepository = Depends(get_repository(ClassRepository)),
        students_repo: StudentRepository = Depends(get_repository(StudentRepository))
    ):
    """Получить все классы преподавателя и учеников этих классов"""
    try:
        await get_user_from_payload(token, users_repo)
        class_data = await class_repo.get_class_by_id(class_id)
        students = await students_repo.get_students_by_class_id(class_id)
        return ClassOut(**class_data.dict(), students=students)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except EntityDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])    

@router.delete('/{class_id}')
async def get_classes(
        class_id: int,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        class_repo: ClassRepository = Depends(get_repository(ClassRepository))
    ):
    """Удалить класс"""
    try:
        await get_user_from_payload(token, users_repo)
        await class_repo.delete(class_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except EntityDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])
        
        
@router.post('/')
async def create_class(
        class_data: ClassIn,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        class_repo: ClassRepository = Depends(get_repository(ClassRepository))
    ):
    """Создать класс"""
    try:
        user = await get_user_from_payload(token, users_repo)
        id = await class_repo.create_class(class_data, teacher_id=user.id)
        return id
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)


@router.put('/')
async def update_class(
        class_data: ClassUpdate,
        token: OAuth2PasswordBearer = Depends(get_oauth2()),
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        class_repo: ClassRepository = Depends(get_repository(ClassRepository))
    ):
    """Изменить название класса"""
    try:
        await get_user_from_payload(token, users_repo)
        await class_repo.update(class_data.id, class_data)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except EntityDoesNotExist as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.args[0])
    