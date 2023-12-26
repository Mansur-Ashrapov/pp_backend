from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime, timedelta


class AppSettings(BaseSettings):
    secret_key: str = (
        "0lCU8ghbHhKCKFBw3UnVlQUyHSXOIKfZN2pdlUoDRkpY6TM6kleGveuIetQo9zS1"
    )
    access_token_expires: timedelta = timedelta(days=1)
    algorithm: str = "HS256"

    database_url: str 
    
config = AppSettings()