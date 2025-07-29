from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(BASE_DIR / ".env.dev")  # 개발 환경
load_dotenv(BASE_DIR / ".env.prod")  # 운영 환경 (dev 위에 덮어씀)


class Settings(BaseSettings):
    openai_api_key: str
    openai_model_name: str = "gpt-3.5-turbo"
    app_env: str = "development"
    debug: bool = True
    elasticsearch_hosts: str = "http://localhost:9200"


settings = Settings()
