from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(BASE_DIR / ".env.prod")  # 운영 환경 (기본값)
load_dotenv(BASE_DIR / ".env.dev")  # 개발 환경 (prod 위에 덮어씀)


class Settings(BaseSettings):
    openai_api_key: str
    openai_model_name: str = "gpt-3.5-turbo"
    gemini_api_key: str
    gemini_model_name: str = "gemini-1.5-flash"
    app_env: str = "development"
    debug: bool = True
    elasticsearch_hosts: str

    google_search_api_key: str
    google_cse_id: str

    embedding_model_name: str = "gemini-embedding-001"
    elasticsearch_index_learning_materials: str = "learning_materials"
    elasticsearch_index_user_feedback: str = "user_concept_understanding_feedback"


settings = Settings()
