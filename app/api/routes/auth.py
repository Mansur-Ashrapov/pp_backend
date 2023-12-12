from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from starlette import status
from jose import jwt, JWTError
from asyncpg.exceptions import UniqueViolationError

from app.db.exceptions import EntityDoesNotExist, EntityAlreadyExist
from app.api.dependecies.database import get_repository
from app.models.schemas.auth import Token
from app.models.schemas.users import UserInDB, UserRegister
from app.db.repositories.users import UserRepository
from app.services.security import verify_password, get_password_hash, create_access_token, decode_token


router = APIRouter()

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

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
    new_user = UserRegister(
        username=user.username,
        password=get_password_hash(user.password),
        fullname=user.fullname,
        email=user.email,
    )
    try:
        await users_repo.create_user(new_user)
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="User with this email or username already exists")
    return {"status_code": 201}


@router.get("/", response_model=UserInDB, response_model_exclude={"password_hash"})
async def protected(
        users_repo: UserRepository = Depends(get_repository(UserRepository)),
        token: OAuth2PasswordBearer = Depends(oauth2_bearer)
    ):
    """ Получить данные о пользователе

    Args:
        token: Необходимо иметь токены авторизации.

    Returns:
        UserInDB: данные о пользователе
    """
    try:
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
        user = await users_repo.get_user_by_username(payload['username'])
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    except EntityDoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist")