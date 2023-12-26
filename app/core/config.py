from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime, timedelta


class AppSettings(BaseSettings):
    access_token_expires: timedelta = timedelta(days=1)
    algorithm: str = "HS256"

    secret_key: str
    database_url: str 

config = AppSettings()