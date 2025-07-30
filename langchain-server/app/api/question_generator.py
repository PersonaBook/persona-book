# app/api/question_generator.py
import base64
import tempfile
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.pdf_service import pdf_service
from app.services.question_generator_service import question_generator_service


router = APIRouter(tags=["Question Generation"])


class QuestionGenerationRequest(BaseModel):
    pdf_base64: str # Base64 인코딩된 PDF 문자열 추가
    query: str
    difficulty: str = "보통"
    question_type: str = "객관식"
    max_pages: Optional[int] = None
    count: int = 1


class QuestionGenerationResponse(BaseModel):
    success: bool
    message: str
    questions: List[str] = []
    chunks_count: int = 0


@router.post("/generate-question", response_model=QuestionGenerationResponse)
async def generate_question(request: QuestionGenerationRequest):
    print(f"🎯 /generate-question 엔드포인트 호출됨 - 이 메시지가 보이면 question_generator.py가 호출된 것입니다!")
    print(f"📊 요청 데이터: query={request.query}, difficulty={request.difficulty}, question_type={request.question_type}")
    """
    PDF를 처리하고 연습문제를 생성합니다.

    - **PDF 처리**: PyMuPDF를 사용하여 PDF 텍스트 추출
    - **청킹**: SemanticChunker를 사용하여 의미적 청킹
    - **임베딩**: OpenAI Embeddings를 사용하여 벡터화
    - **벡터 스토어**: Elasticsearch에 임베딩 저장
    - **문제 생성**: RAG를 사용하여 관련 컨텍스트 기반 문제 생성

    **성능 최적화**: 캐싱 시스템으로 두 번째 요청부터 속도 향상
    """
    temp_file_path = None
    try:
        # 1. Base64 문자열을 PDF 파일로 디코딩하여 임시 파일로 저장
        pdf_data = base64.b64decode(request.pdf_base64)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_data)
            temp_file_path = temp_file.name

        # 2. PDF 처리 및 청킹
        pdf_service_instance = pdf_service()
        chunks = pdf_service_instance.process_pdf_and_create_chunks(
            temp_file_path,
            max_pages=request.max_pages
        )

        if not chunks:
            return QuestionGenerationResponse(
                success=False,
                message="PDF 처리에 실패했습니다.",
                chunks_count=0
            )

        # 3. 벡터 스토어 설정
        success = question_generator_service.setup_vector_store(chunks)
        if not success:
            return QuestionGenerationResponse(
                success=False,
                message="벡터 스토어 설정에 실패했습니다.",
                chunks_count=len(chunks)
            )

        # 4. 연습문제 생성
        if request.count == 1:
            question = question_generator_service.generate_question_with_rag(
                request.query,
                request.difficulty,
                request.question_type
            )
            questions = [question]
        else:
            questions = question_generator_service.generate_multiple_questions(
                request.query,
                request.count,
                request.difficulty
            )

        return QuestionGenerationResponse(
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





@router.post("/test-pdf-processing")
async def test_pdf_processing(pdf_base64: str, max_pages: int = 5):
    """
    PDF 처리 기능을 테스트합니다.

    PDF 파일의 텍스트 추출, 청킹, 임베딩 과정을 테스트하고 결과를 반환합니다.

    **테스트 과정**:
    1. PDF 텍스트 추출 (PyMuPDF)
    2. 텍스트 정제 및 전처리
    3. 의미적 청킹 (SemanticChunker)
    4. 임베딩 생성 (OpenAI)

    **응답**: 처리된 청크 수와 샘플 청크 내용
    """
    temp_file_path = None
    try:
        pdf_data = base64.b64decode(pdf_base64)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_data)
            temp_file_path = temp_file.name

        pdf_service_instance = pdf_service()
        chunks = pdf_service_instance.process_pdf_and_create_chunks(temp_file_path, max_pages)

        return {
            "success": True,
            "message": f"PDF 처리 테스트 완료",
            "chunks_count": len(chunks),
            "sample_chunk": chunks[0].page_content[:200] + "..." if chunks else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 처리 테스트 중 오류가 발생했습니다: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)