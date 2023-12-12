import databases
import sqlalchemy
import uvicorn

from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.tables import metadata
from app.core.config import config
from app.core import events
from app.api import api


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = sqlalchemy.create_engine(
        config.database_url
    )
    metadata.create_all(engine)
    app.state.database = databases.Database(config.database_url)

    await events.connect_to_db(app)
    yield
    await events.close_db_connection(app)

app = FastAPI(lifespan=lifespan)

app.include_router(api.router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)