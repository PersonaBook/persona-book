"""
로컬 임베딩을 사용하는 문제 생성 API
"""
import base64
import tempfile
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.local_pdf_service import get_local_pdf_service
from app.services.local_question_generator import get_local_question_generator_service


router = APIRouter(tags=["Local Question Generation"])


class LocalQuestionGenerationRequest(BaseModel):
    pdf_base64: str
    query: str
    difficulty: str = "보통"
    question_type: str = "객관식"
    max_pages: Optional[int] = None
    count: int = 1


class LocalQuestionGenerationResponse(BaseModel):
    success: bool
    message: str
    questions: List[str] = []
    chunks_count: int = 0


@router.post("/local-generate-question", response_model=LocalQuestionGenerationResponse)
async def local_generate_question(request: LocalQuestionGenerationRequest):
    """
    로컬 임베딩을 사용하여 PDF를 처리하고 연습문제를 생성합니다.

    - **PDF 처리**: PyMuPDF를 사용하여 PDF 텍스트 추출
    - **청킹**: RecursiveCharacterTextSplitter를 사용하여 텍스트 분할
    - **임베딩**: SentenceTransformers를 사용하여 로컬 임베딩 생성
    - **문제 생성**: 로컬 임베딩 기반 RAG를 사용하여 문제 생성

    **장점**: OpenAI API 할당량에 의존하지 않음
    """
    temp_file_path = None
    try:
        # 1. Base64 문자열을 PDF 파일로 디코딩하여 임시 파일로 저장
        pdf_data = base64.b64decode(request.pdf_base64)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_data)
            temp_file_path = temp_file.name

        # 2. PDF 처리 및 청킹
        local_pdf_service = get_local_pdf_service()
        chunks = local_pdf_service.process_pdf_and_create_chunks(
            temp_file_path,
            max_pages=request.max_pages
        )

        if not chunks:
            return LocalQuestionGenerationResponse(
                success=False,
                message="PDF 처리에 실패했습니다.",
                chunks_count=0
            )

        # 3. 로컬 문제 생성 서비스 설정
        local_question_service = get_local_question_generator_service()
        success = local_question_service.setup_documents(chunks)
        if not success:
            return LocalQuestionGenerationResponse(
                success=False,
                message="문서 설정에 실패했습니다.",
                chunks_count=len(chunks)
            )

        # 4. 연습문제 생성
        if request.count == 1:
            result = local_question_service.generate_question_with_rag(
                request.query,
                request.difficulty,
                request.question_type
            )
            
            if result["success"]:
                question_text = f"문제: {result['question']}\n정답: {result['answer']}\n해설: {result['explanation']}"
                questions = [question_text]
            else:
                return LocalQuestionGenerationResponse(
                    success=False,
                    message=result["message"],
                    chunks_count=len(chunks)
                )
        else:
            questions = local_question_service.generate_multiple_questions(
                request.query,
                request.count,
                request.difficulty
            )

        return LocalQuestionGenerationResponse(
            success=True,
            message="연습문제 생성이 완료되었습니다.",
            questions=questions,
            chunks_count=len(chunks)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연습문제 생성 중 오류가 발생했습니다: {str(e)}")
    finally:
        # 임시 파일 삭제
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@router.get("/local-ping")
def local_ping():
    """
    로컬 문제 생성 API 헬스 체크
    """
    return {"status": "ok", "message": "Local Question Generator API is running"}


@router.post("/local-test-pdf-processing")
async def local_test_pdf_processing(pdf_base64: str, max_pages: int = 5):
    """
    로컬 PDF 처리 기능을 테스트합니다.
    """
    temp_file_path = None
    try:
        pdf_data = base64.b64decode(pdf_base64)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_data)
            temp_file_path = temp_file.name

        local_pdf_service = get_local_pdf_service()
        chunks = local_pdf_service.process_pdf_and_create_chunks(temp_file_path, max_pages)

        return {
            "success": True,
            "message": f"로컬 PDF 처리 테스트 완료",
            "chunks_count": len(chunks),
            "sample_chunk": chunks[0].page_content[:200] + "..." if chunks else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"로컬 PDF 처리 테스트 중 오류가 발생했습니다: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path) 