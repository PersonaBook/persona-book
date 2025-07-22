from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv(".env.dev")   # 첫 번째 파일
load_dotenv(".env.prod")  # 두 번째 파일, dev 값 위에 업로드/덮어쓰기

class Settings(BaseSettings):
    openai_api_key: str
    openai_model_name: str = "gpt-3.5-turbo"
    app_env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    class Config:
        env_file = None  # env_file 미지정, 대신 python-dotenv로 직접 환경변수 주입

settings = Settings()