from app.db.exceptions import EntityDoesNotExist
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime
from fastapi.exceptions import HTTPException
from starlette import status

from app.models.schemas.users import User
from app.db.repositories.users import UserRepository
from app.core.config import config


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(username: str, user_id: str):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.utcnow() + config.access_token_expires
    encode.update({'exp': expires})
    return jwt.encode(encode, config.secret_key, algorithm=config.algorithm)

def decode_token(token):
    payload = jwt.decode(token, config.secret_key, algorithms=[config.algorithm])
    username = payload.get('sub')
    user_id = payload.get('id')
    if not username and not user_id:
        return None
    return {'username': username, 'user_id': user_id}

async def get_user_from_payload(token, users_repo: UserRepository) -> User:
    try:
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
        user = await users_repo.get_user_by_username(payload['username'])
        return User(**user.dict(exclude='password_hash'))
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user")
    except EntityDoesNotExist:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User does not exist")