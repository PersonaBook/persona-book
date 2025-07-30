"""
향상된 로컬 임베딩을 사용하는 문제 생성 API
"""
import base64
import tempfile
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.local_pdf_service import get_local_pdf_service
from app.services.enhanced_local_question_generator import get_enhanced_local_question_generator_service


router = APIRouter(tags=["Enhanced Local Question Generation"])


class EnhancedQuestionGenerationRequest(BaseModel):
    pdf_base64: str
    query: str
    difficulty: str = "보통"
    question_type: str = "객관식"
    max_pages: Optional[int] = None
    count: int = 1


class EnhancedQuestionGenerationResponse(BaseModel):
    success: bool
    message: str
    questions: List[str] = []
    chunks_count: int = 0
    chapter: Optional[str] = None
    concept_keywords: List[str] = []


class KeywordSearchRequest(BaseModel):
    keyword: str


class KeywordSearchResponse(BaseModel):
    success: bool
    message: str
    results: List[Dict[str, Any]] = []


@router.post("/enhanced-local-generate-question", response_model=EnhancedQuestionGenerationResponse)
async def enhanced_local_generate_question(request: EnhancedQuestionGenerationRequest):
    print(f"🎯 /enhanced-local-generate-question 엔드포인트 호출됨 - 이 메시지가 보이면 enhanced_local_question_generator.py가 호출된 것입니다!")
    print(f"📊 요청 데이터: query={request.query}, difficulty={request.difficulty}, question_type={request.question_type}")
    """
    향상된 로컬 임베딩을 사용하여 PDF를 처리하고 연습문제를 생성합니다.

    - **PDF 처리**: PyMuPDF를 사용하여 PDF 텍스트 추출
    - **청킹**: RecursiveCharacterTextSplitter를 사용하여 텍스트 분할
    - **임베딩**: SentenceTransformers를 사용하여 로컬 임베딩 생성
    - **문제 생성**: 챕터별 문제 템플릿과 키워드 데이터를 활용한 문제 생성
    - **키워드 검색**: keywords.json을 활용한 키워드 기반 검색

    **장점**: 
    - OpenAI API 할당량에 의존하지 않음
    - 챕터별 맞춤형 문제 생성
    - 키워드 기반 정확한 컨텍스트 매핑
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
            return EnhancedQuestionGenerationResponse(
                success=False,
                message="PDF 처리에 실패했습니다.",
                chunks_count=0
            )

        # 3. 향상된 로컬 문제 생성 서비스 설정
        enhanced_question_service = get_enhanced_local_question_generator_service()
        success = enhanced_question_service.setup_documents(chunks)
        if not success:
            return EnhancedQuestionGenerationResponse(
                success=False,
                message="문서 설정에 실패했습니다.",
                chunks_count=len(chunks)
            )

        # 4. 연습문제 생성
        if request.count == 1:
            result = enhanced_question_service.generate_question_with_rag(
                request.query,
                request.difficulty,
                request.question_type
            )
            
            if result["success"]:
                question_text = f"문제: {result['question']}\n정답: {result['answer']}\n해설: {result['explanation']}"
                questions = [question_text]
                chapter = result.get("chapter")
                concept_keywords = result.get("concept_keywords", [])
            else:
                return EnhancedQuestionGenerationResponse(
                    success=False,
                    message=result["message"],
                    chunks_count=len(chunks)
                )
        else:
            questions = enhanced_question_service.generate_multiple_questions(
                request.query,
                request.count,
                request.difficulty
            )
            chapter = None
            concept_keywords = []

        return EnhancedQuestionGenerationResponse(
            success=True,
            message="연습문제 생성이 완료되었습니다.",
            questions=questions,
            chunks_count=len(chunks),
            chapter=chapter,
            concept_keywords=concept_keywords
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연습문제 생성 중 오류가 발생했습니다: {str(e)}")
    finally:
        # 임시 파일 삭제
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@router.post("/keyword-search", response_model=KeywordSearchResponse)
async def keyword_search(request: KeywordSearchRequest):
    """
    키워드로 페이지를 검색합니다.
    """
    try:
        enhanced_question_service = get_enhanced_local_question_generator_service()
        results = enhanced_question_service.search_keywords(request.keyword)
        
        if results:
            return KeywordSearchResponse(
                success=True,
                message=f"'{request.keyword}' 검색 결과: {len(results)}개",
                results=results
            )
        else:
            return KeywordSearchResponse(
                success=False,
                message=f"'{request.keyword}'에 대한 검색 결과가 없습니다.",
                results=[]
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 검색 중 오류가 발생했습니다: {str(e)}")


@router.get("/enhanced-local-ping")
def enhanced_local_ping():
    """
    향상된 로컬 문제 생성 API 헬스 체크
    """
    return {"status": "ok", "message": "Enhanced Local Question Generator API is running"}


@router.get("/chapter-info")
def get_chapter_info():
    """
    챕터별 페이지 정보를 반환합니다.
    """
    enhanced_question_service = get_enhanced_local_question_generator_service()
    return {
        "status": "ok",
        "chapters": enhanced_question_service.chapter_pages,
        "total_keywords": len(enhanced_question_service.keywords_data)
    }


@router.post("/enhanced-test-pdf-processing")
async def enhanced_test_pdf_processing(pdf_base64: str, max_pages: int = 5):
    """
    향상된 로컬 PDF 처리 기능을 테스트합니다.
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
            "message": f"향상된 로컬 PDF 처리 테스트 완료",
            "chunks_count": len(chunks),
            "sample_chunk": chunks[0].page_content[:200] + "..." if chunks else None
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"향상된 로컬 PDF 처리 테스트 중 오류가 발생했습니다: {str(e)}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path) 