from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    openai_api_key: str
    openai_model_name: str = "gpt-3.5-turbo"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()