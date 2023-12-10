from pydantic import BaseModel


class Token(BaseModel):
    username: str
    password: str


class Login(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

