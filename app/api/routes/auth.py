from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from starlette import status
from asyncpg.exceptions import UniqueViolationError

from app.db.exceptions import EntityDoesNotExist
from app.api.dependecies.database import get_repository
from app.api.dependecies.auth import get_oauth2
from app.models.schemas.auth import Token
from app.models.schemas.users import User, UserRegister, UserUpdateFullName, UserUpdatePassword, UserUpdatePasswordHash
from app.db.repositories.users import UserRepository
from app.services.security import verify_password, get_password_hash, create_access_token, get_user_from_payload


router = APIRouter()

@router.post("/token", response_model=Token)
async def login(
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)
    ):
    """Вход на сайт

    Raises:
        HTTPException: 400 плохой username or password

    Returns:
        Token: содержит токены авторизации
    """
    try:
        db_user = await users_repo.get_user_by_username(form_data.username)
    except EntityDoesNotExist:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad username or password")
    
    if not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad username or password")
    
    token = create_access_token(db_user.username, db_user.id)
    return {'access_token': token, 'token_type': 'bearer'}
    

@router.post("/")
async def register(user: UserRegister, users_repo: UserRepository = Depends(get_repository(UserRepository))):
    """ Зарегистрировать пользователя 

    Args:
        user (UserRegister): Данные для создания пользователя
    """
    try:
        new_user = UserRegister(
            username=user.username,
            password=get_password_hash(user.password),
            fullname=user.fullname,
            email=user.email,
        )
        await users_repo.create_user(new_user)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")
    return {"status_code": 201}


@router.delete("/")
async def delete(token: OAuth2PasswordBearer = Depends(get_oauth2()), users_repo: UserRepository = Depends(get_repository(UserRepository))):
    """ Удалить пользователя

        нужно только отправить запрос DELETE с токеном
    """
    try:
        user = await get_user_from_payload(token, users_repo)
        users_repo.delete(user.id)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")
    return {"status_code": 201}


@router.get("/", response_model=User)
async def get_info_about_user(
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        token: OAuth2PasswordBearer = Depends(get_oauth2())
    ):
    """ Получить данные о пользователе

    Args:
        token: Необходимо иметь токены авторизации.

    Returns:
        User: данные о пользователе
    """
    try:
        user = await get_user_from_payload(token, users_repo)
        return user
    except EntityDoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist")
    
@router.put("/fullname")
async def update_fullname_user(
        user_update: UserUpdateFullName,
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        token: OAuth2PasswordBearer = Depends(get_oauth2())
    ):
    """Поменять ФИО преподавателя
    """
    try:
        user = await get_user_from_payload(token, users_repo)
        await users_repo.update(user_update, user.id)
    except EntityDoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    
@router.put("/password")
async def update_password_user(
        user_update: UserUpdatePassword,
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        token: OAuth2PasswordBearer = Depends(get_oauth2())
    ):
    """
    Поменять пароль пользователя
    """
    try:
        user = await get_user_from_payload(token, users_repo)
        user_update = UserUpdatePasswordHash(password_hash=get_password_hash(user_update.password))
        await users_repo.update(user_update, user.id)
    except EntityDoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist")
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    