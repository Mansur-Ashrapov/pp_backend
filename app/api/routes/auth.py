from fastapi import APIRouter, Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from fastapi.exceptions import HTTPException

from app.db.exceptions import EntityDoesNotExist, EntityAlreadyExist
from app.api.dependecies.database import get_repository
from app.models.schemas.auth import Login, Token
from app.models.schemas.users import UserInDB, UserRegister
from app.db.repositories.users import UserRepository
from app.services.security import verify_password


router = APIRouter()


@router.post("/login", response_model=Login)
async def login(
        user: Token,
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        authorize: AuthJWT = Depends()
    ):
    """Вход на сайт

    Raises:
        HTTPException: 404 пользователь с данным username не найден
        HTTPException: 401 плохой username or password

    Returns:
        Login: содержит токены авторизации
    """
    try:
        db_user = await users_repo.get_user_by_username(user.username)
    except EntityDoesNotExist:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.username and user.password:
        if db_user and verify_password(user.password, db_user.password_hash):
            access_token = authorize.create_access_token(subject=user.username)
            refresh_token = authorize.create_refresh_token(subject=user.username)
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
    raise HTTPException(status_code=401, detail="Bad username or password")


@router.post("/refresh", response_model=Login)
async def refresh(authorize: AuthJWT = Depends()):
    """ Обновить токены авторизации

    Args:
        authorize (AuthJWT): Необходимо иметь токены авторизации.

    Returns:
        Login: содержит токены авторизации
    """
    authorize.jwt_refresh_token_required()

    current_user = authorize.get_jwt_subject()
    new_refresh_token = authorize.create_refresh_token(subject=current_user)
    new_access_token = authorize.create_access_token(subject=current_user)
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer" }


@router.get("/me", response_model=UserInDB, response_model_exclude={"password_hash"})
async def protected(authorize: AuthJWT = Depends(), users_repo: UserRepository = Depends(get_repository(UserRepository))):
    """ Получить данные о пользователе

    Args:
        authorize (AuthJWT): Необходимо иметь токены авторизации.

    Returns:
        UserInDB: данные о пользователе
    """
    authorize.jwt_required()

    current_user = authorize.get_jwt_subject()
    user = await users_repo.get_user_by_username(current_user)
    return user


@router.post("/register")
async def register(user: UserRegister, users_repo: UserRepository = Depends(get_repository(UserRepository))):
    """ Зарегистрировать пользователя 

    Args:
        user (UserRegister): Данные для создания пользователя
    """
    new_user = UserRegister(
        username=user.username,
        password=user.password,
        email=user.email,
    )
    try:
        await users_repo.create_user(new_user)
    except EntityAlreadyExist:
        raise HTTPException(status_code=401, detail="User with this email or username already exists")
    return {"status_code": 201}