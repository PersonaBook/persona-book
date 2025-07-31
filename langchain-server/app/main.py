import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# 환경 변수 로드 (프로젝트 루트의 .env.prod 파일)
load_dotenv('../.env.prod')  # langchain-server 디렉토리에서 상위로 이동
load_dotenv('.env.prod')     # 현재 디렉토리도 확인

from app.api.chat_history import router as chat_history_router
from app.api.openai_chat import router as openai_chat_router

# 새로운 분리된 API들
from app.api.question_generation_api import router as question_generation_router
from app.api.answer_evaluation_api import router as answer_evaluation_router
from app.api.concept_explanation_api import router as concept_explanation_router
from app.api.page_search_new_api import router as page_search_new_router
from app.api.pdf_upload_api import router as pdf_upload_router

# 제거된 파일들의 import는 삭제됨

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.elasticsearch_client import ElasticsearchClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 초기화/정리 작업"""
    print("🚀 애플리케이션 시작 중...")
    
    # Elasticsearch 클라이언트 초기화
    try:
        await ElasticsearchClient.initialize()
        print("✅ Elasticsearch 클라이언트 초기화 완료")
    except Exception as e:
        print(f"❌ Elasticsearch 클라이언트 초기화 실패: {e}")
    
    # 기타 초기화 작업들
    print("✅ 애플리케이션 초기화 완료")
    
    yield
    
    # 정리 작업
    print("🔄 애플리케이션 종료 중...")
    try:
        await ElasticsearchClient.close()
        print("✅ Elasticsearch 클라이언트 정리 완료")
    except Exception as e:
        print(f"❌ Elasticsearch 클라이언트 정리 실패: {e}")
    print("✅ 애플리케이션 종료 완료")

app = FastAPI(
    title="LangChain RAG API Server",
    description="RAG 기반 학습 지원 API 서버",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기타 API 라우터들 (먼저 등록)
app.include_router(openai_chat_router, prefix="/api/v1")
app.include_router(chat_history_router, prefix="/api/v1")

# ===== 새로운 분리된 API들 =====
app.include_router(question_generation_router, prefix="/api/v1", tags=["Question Generation"])
app.include_router(answer_evaluation_router, prefix="/api/v1", tags=["Answer Evaluation"])
app.include_router(concept_explanation_router, prefix="/api/v1", tags=["Concept Explanation"])
app.include_router(page_search_new_router, prefix="/api/v1", tags=["Page Search"])
app.include_router(pdf_upload_router, prefix="/api/v1", tags=["PDF Upload"])

# 제거된 라우터들은 등록하지 않음

# 제거된 라우터들은 등록하지 않음


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Chat API Server is running!",
        "apis": [
            "GENERATING_QUESTION",
            "GENERATING_ADDITIONAL_QUESTION",
            "EVALUATING_ANSWER_AND_LOGGING",
            "PRESENTING_CONCEPT_EXPLANATION",
            "REEXPLAINING_CONCEPT",
            "PROCESSING_PAGE_SEARCH_RESULT"
        ]
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-15T10:30:00Z"
    }


@app.get("/api/v1/ping")
async def ping():
    """Spring Boot에서 연결 확인용 ping 엔드포인트"""
    return {"message": "pong"}