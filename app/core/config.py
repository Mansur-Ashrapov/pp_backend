from pydantic import BaseModel
from datetime import datetime, timedelta


class AppSettings(BaseModel):
    secret_key: str = (
        "0lCU8ghbHhKCKFBw3UnVlQUyHSXOIKfZN2pdlUoDRkpY6TM6kleGveuIetQo9zS1"
    )
    access_token_expires: timedelta = timedelta(days=1)
    algorithm: str = "HS256"

    database_url: str = "postgresql://postgres:postgres@0.0.0.0:5432/postgres"

    # class Config:
    #     env_file = '.env'

config = AppSettings()