from databases import Database
from fastapi import FastAPI
# from loguru import logger

from app.core.config import AppSettings


async def connect_to_db(app: FastAPI) -> None:
    await app.state.database.connect()


async def close_db_connection(app: FastAPI) -> None:
    await app.state.database.disconnect()