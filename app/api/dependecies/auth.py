from fastapi.security import OAuth2PasswordBearer

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

def get_oauth2() -> OAuth2PasswordBearer:
    return oauth2_bearer