from fastapi import APIRouter, HTTPException
from app.schemas.request.rag_apis import GeneratingQuestionRequest
from app.schemas.response.rag_apis import GeneratingQuestionResponse
from app.services.question_generator_service import question_generator_service
import time

router = APIRouter(tags=["Question Generation"])


@router.post("/generating-question", response_model=GeneratingQuestionResponse)
async def generating_question(request: GeneratingQuestionRequest):
    """RAG를 사용하여 문제를 생성합니다."""
    start_time = time.time()
    
    try:
        # PDF 처리 및 청킹
        chunks = question_generator_service.process_pdf_and_create_chunks(
            request.pdf_base64, 
            max_pages=request.max_pages
        )
        
        if not chunks:
            return GeneratingQuestionResponse(
                success=False,
                message="PDF 처리에 실패했습니다.",
                userId=request.userId,
                bookId=request.bookId,
                question="",
                correct_answer="",
                explanation="",
                difficulty=request.difficulty.value,
                question_type=request.question_type.value,
                chunks_used=0,
                processing_time=time.time() - start_time
            )
        
        # 벡터 스토어 설정
        success = question_generator_service.setup_vector_store(chunks)
        if not success:
            return GeneratingQuestionResponse(
                success=False,
                message="벡터 스토어 설정에 실패했습니다.",
                userId=request.userId,
                bookId=request.bookId,
                question="",
                correct_answer="",
                explanation="",
                difficulty=request.difficulty.value,
                question_type=request.question_type.value,
                chunks_used=len(chunks),
                processing_time=time.time() - start_time
            )
        
        # 문제 생성
        result = question_generator_service.generate_question_with_rag(
            request.query,
            request.difficulty.value,
            request.question_type.value
        )
        
        if isinstance(result, dict) and result.get("success", False):
            return GeneratingQuestionResponse(
                success=True,
                message="문제 생성이 완료되었습니다.",
                userId=request.userId,
                bookId=request.bookId,
                question=result.get("question", ""),
                correct_answer=result.get("correct_answer", ""),
                explanation=result.get("explanation", ""),
                difficulty=request.difficulty.value,
                question_type=request.question_type.value,
                chunks_used=len(chunks),
                processing_time=time.time() - start_time
            )
        else:
            return GeneratingQuestionResponse(
                success=False,
                message="문제 생성에 실패했습니다.",
                userId=request.userId,
                bookId=request.bookId,
                question="",
                correct_answer="",
                explanation="",
                difficulty=request.difficulty.value,
                question_type=request.question_type.value,
                chunks_used=len(chunks),
                processing_time=time.time() - start_time
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문제 생성 중 오류가 발생했습니다: {str(e)}") 