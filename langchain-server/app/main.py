from contextlib import asynccontextmanager

from app.api.learning import router as learning_router
from app.api.pdf_upload_api import router as pdf_upload_router
from app.api.question_generation_api import router as question_generator_router
from app.api.ping import router as ping_router
from app.api.answer_evaluation_api import router as answer_evaluation_router
from app.api.page_search_new_api import router as page_search_router
from app.core.elasticsearch_client import ElasticsearchClient
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import json
from app.tools.learning_material_search_tool import get_learning_material_search_tool
from app.tools.google_search_tool import get_google_search_tool
from app.tools.explanation_generator_tool import get_explanation_generator_tool
from app.agents.learning_agent import LearningAgent
from app.repository.learning_material_repository import LearningMaterialRepository
from app.services.learning_service import LearningService
from app.services.embedding_service import EmbeddingService


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ElasticsearchClient.initialize()

    es_client = await ElasticsearchClient.get_client()
    embedding_service = EmbeddingService()
    await embedding_service.ainitialize()
    learning_material_repo = LearningMaterialRepository(es_client, embedding_service)
    await learning_material_repo.create_index()
    learning_service = LearningService(learning_material_repo)

    app.state.learning_material_search_tool = await get_learning_material_search_tool()
    app.state.google_search_tool = await get_google_search_tool()
    app.state.explanation_generator_tool = await get_explanation_generator_tool()

    app.state.learning_agent = LearningAgent(learning_service)
    await app.state.learning_agent.ainitialize()

    yield
    await ElasticsearchClient.close()


# UTF-8 안전 처리 미들웨어
class UTF8SafeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            # 요청 본문 읽기
            body = await request.body()

            if body:
                try:
                    # JSON 파싱 시도
                    json_data = json.loads(body.decode('utf-8'))

                    # content 필드가 있으면 안전하게 처리
                    if isinstance(json_data, dict) and 'content' in json_data:
                        content = json_data['content']
                        if isinstance(content, str):
                            # 특수문자 안전 처리
                            json_data['content'] = content.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')

                            # 새로운 body로 요청 재구성
                            new_body = json.dumps(json_data, ensure_ascii=False).encode('utf-8')

                            # 새로운 요청 생성
                            from starlette.requests import Request as StarletteRequest
                            scope = request.scope.copy()

                            async def new_receive():
                                return {"type": "http.request", "body": new_body}

                            request = StarletteRequest(scope, new_receive)

                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    print(f"🚨 JSON/UTF-8 처리 오류: {e}")
                    pass  # 원본 요청 그대로 진행

            response = await call_next(request)
            return response
        except Exception as e:
            print(f"🚨 미들웨어 오류: {e}")
            return JSONResponse(
                status_code=400,
                content={"detail": "요청 처리 중 인코딩 오류가 발생했습니다."}
            )

app = FastAPI(lifespan=lifespan)

# UTF-8 안전 처리 미들웨어 추가 (CORS보다 먼저)
app.add_middleware(UTF8SafeMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RequestValidationError 핸들러 - UTF-8 디코딩 에러를 직접 처리
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(f"🚨 커스텀 Validation 핸들러 호출됨: {exc}")
    print(f"🚨 Exception 타입: {type(exc)}")
    print(f"🚨 Exception 에러들: {exc.errors()}")

    # FastAPI 내부에서 발생한 UnicodeDecodeError 처리
    error_messages = [str(error) for error in exc.errors()]
    if any("UnicodeDecodeError" in msg or "codec can't decode" in msg for msg in error_messages):
        print("🚨 UTF-8 관련 에러 감지됨 - 안전한 응답 반환")
        return JSONResponse(
            status_code=400,
            content={"detail": "PDF 파일 업로드 중 인코딩 오류가 발생했습니다. 파일을 다시 선택해주세요."}
        )

    # multipart form-data 관련 오류 처리
    if any("model_attributes_type" in str(error) for error in exc.errors()):
        print("🚨 multipart 데이터 검증 오류 - PDF 업로드 관련으로 추정")
        return JSONResponse(
            status_code=400,
            content={"detail": "PDF 파일 형식에 문제가 있습니다. 올바른 PDF 파일을 업로드해주세요."}
        )

    return JSONResponse(
        status_code=422,
        content={"detail": "입력 데이터 검증에 실패했습니다.", "errors": str(exc.errors())}
    )

# UTF-8 디코딩 에러 핸들러
@app.exception_handler(UnicodeDecodeError)
async def unicode_decode_error_handler(request: Request, exc: UnicodeDecodeError):
    print(f"🚨 UTF-8 디코딩 오류 발생: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": "텍스트 인코딩 오류가 발생했습니다. 입력 데이터를 확인해주세요."}
    )

# 일반적인 예외 핸들러
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    print(f"🚨 일반 오류 발생: {type(exc).__name__}: {exc}")
    if "UnicodeDecodeError" in str(exc) or "codec can't decode" in str(exc):
        return JSONResponse(
            status_code=400,
            content={"detail": "텍스트 인코딩 오류가 발생했습니다. 특수문자 처리에 문제가 있을 수 있습니다."}
        )
    return JSONResponse(
        status_code=500,
        content={"detail": f"서버 내부 오류가 발생했습니다: {str(exc)}"}
    )


app.include_router(
    learning_router, prefix="/api/v1/learning", tags=["Learning Materials"]
)
app.include_router(pdf_upload_router, prefix="/api/v1", tags=["PDF Upload"])
app.include_router(question_generator_router, prefix="/api/v1")
app.include_router(ping_router, prefix="/api/v1", tags=["Health Check"])
app.include_router(answer_evaluation_router, prefix="/api/v1", tags=["Answer Evaluation"])
app.include_router(page_search_router, prefix="/api/v1", tags=["Page Search"])
