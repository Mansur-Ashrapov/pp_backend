from pydantic import BaseModel
from datetime import datetime, timedelta


class AppSettings(BaseModel):
    authjwt_secret_key: str = (
        "0lCU8ghbHhKCKFBw3UnVlQUyHSXOIKfZN2pdlUoDRkpY6TM6kleGveuIetQo9zS1"
    )
    authjwt_access_token_expires: timedelta = timedelta(hours=1)
    authjwt_refresh_token_expires: timedelta = timedelta(days=30)

    database_url: str = "someUrl"

    class Config:
        env_file = '.env'