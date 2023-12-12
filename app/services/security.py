from jose import jwt

from passlib.context import CryptContext
from datetime import timedelta, datetime

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
