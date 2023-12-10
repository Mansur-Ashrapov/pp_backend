import databases

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from app.core.config import AppSettings
from app.core import events
from app.api import api


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database = databases.Database(appSettings.database_url)
    await events.connect_to_db(app)
    yield
    await events.close_db_connection(app)

app = FastAPI(lifespan=lifespan)
appSettings = AppSettings()

app.include_router(api.router)



@AuthJWT.load_config
def get_config():
    return appSettings


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})