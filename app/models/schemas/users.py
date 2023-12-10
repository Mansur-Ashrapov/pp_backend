from pydantic import BaseModel


class User(BaseModel):
    username: str
    fullname: str
    email: str

class UserInDB(User):
    id: str
    password_hash: str

class UserRegister(User):
    password: str
