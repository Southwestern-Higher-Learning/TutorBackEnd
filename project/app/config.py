import datetime
import json
import logging
import os
from functools import lru_cache
from typing import List

from pydantic import AnyUrl, BaseSettings

log = logging.getLogger("uvicorn")


class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "dev")
    testing: bool = os.getenv("TESTING", 0)
    database_url: AnyUrl = os.environ.get("DATABASE_URL")
    google_client_id: str = os.getenv("GOOGLE_CLIENT_ID")
    google_project_id: str = os.getenv("GOOGLE_PROJECT_ID")
    google_client_secret: str = os.getenv("GOOGLE_CLIENT_SECRET")
    google_redirect_uris: List[str] = json.loads(
        os.getenv("GOOGLE_REDIRECT_URIS", "[]")
    )
    google_js_origins: List[str] = json.loads(os.getenv("GOOGLE_JS_ORIGINS", "[]"))
    top_domain: str = os.getenv("TOP_DOMAIN")
    authjwt_secret_key: str = "secret"
    authjwt_refresh_token_expires = False
    authjwt_access_token_expires = datetime.timedelta(hours=12)


@lru_cache()
def get_settings() -> Settings:
    log.info("Loading config settings from the environment...")
    return Settings()
