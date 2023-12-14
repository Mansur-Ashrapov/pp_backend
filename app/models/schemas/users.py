from pydantic import BaseModel

class User(BaseModel):
    id: str
    username: str
    fullname: str
    email: str

class UserInDB(User):
    password_hash: str

class UserRegister(BaseModel):
    username: str
    fullname: str
    email: str
    password: str

class UserUpdateFullName(BaseModel):
    fullname: str

class UserUpdatePassword(BaseModel):
    password: str

class UserUpdatePasswordHash(BaseModel):
    password_hash: str
