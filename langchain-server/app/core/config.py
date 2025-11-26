from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(BASE_DIR / ".env.prod")  # 운영 환경 (기본값)
load_dotenv(BASE_DIR / ".env.dev")  # 개발 환경 (prod 위에 덮어씀)


class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    gemini_api_key: str
    google_search_api_key: str
    google_cse_id: str
    
    # Model Configuration
    openai_model_name: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-3-small"
    gemini_model_name: str = "gemini-1.5-flash"
    gemini_flash_exp_model: str = "gemini-2.0-flash-exp"
    embedding_model_name: str = "gemini-embedding-001"
    
    # Application Settings
    app_env: str = "development"
    debug: bool = True
    
    # Elasticsearch Configuration
    elasticsearch_hosts: str
    elasticsearch_url: str = "http://elasticsearch:9200"
    
    # Elasticsearch Indices
    elasticsearch_index_learning_materials: str = "learning_materials"
    elasticsearch_index_user_feedback: str = "user_concept_understanding_feedback"
    elasticsearch_index_pdf_docs: str = "java_learning_docs"
    
    # LLM Configuration
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    rag_search_k: int = 5


settings = Settings()
