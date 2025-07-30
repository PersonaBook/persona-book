from fastapi import APIRouter, HTTPException
from app.schemas.request.rag_apis import GeneratingAdditionalQuestionRequest
from app.schemas.response.rag_apis import GeneratingAdditionalQuestionResponse
from app.services.question_generator_service import question_generator_service
import time

router = APIRouter(tags=["Additional Question Generation"])


@router.post("/generating-additional-question", response_model=GeneratingAdditionalQuestionResponse)
async def generating_additional_question(request: GeneratingAdditionalQuestionRequest):
    """RAG를 사용하여 추가 문제를 생성합니다."""
    start_time = time.time()
    
    try:
        # PDF 처리 및 청킹
        chunks = question_generator_service.process_pdf_and_create_chunks(
            request.pdf_base64, 
            max_pages=request.max_pages
        )
        
        if not chunks:
            return GeneratingAdditionalQuestionResponse(
                success=False,
                message="PDF 처리에 실패했습니다.",
                userId=request.userId,
                bookId=request.bookId,
                additional_question="",
                correct_answer="",
                explanation="",
                difficulty=request.difficulty.value,
                question_type=request.previous_question_type.value,
                chunks_used=0,
                processing_time=time.time() - start_time
            )
        
        # 벡터 스토어 설정
        success = question_generator_service.setup_vector_store(chunks)
        if not success:
            return GeneratingAdditionalQuestionResponse(
                success=False,
                message="벡터 스토어 설정에 실패했습니다.",
                userId=request.userId,
                bookId=request.bookId,
                additional_question="",
                correct_answer="",
                explanation="",
                difficulty=request.difficulty.value,
                question_type=request.previous_question_type.value,
                chunks_used=len(chunks),
                processing_time=time.time() - start_time
            )
        
        # 추가 문제 생성
        result = question_generator_service.generate_question_with_rag(
            request.query,
            request.difficulty.value,
            request.previous_question_type.value
        )
        
        if isinstance(result, dict) and result.get("success", False):
            return GeneratingAdditionalQuestionResponse(
                success=True,
                message="추가 문제 생성이 완료되었습니다.",
                userId=request.userId,
                bookId=request.bookId,
                additional_question=result.get("question", ""),
                correct_answer=result.get("correct_answer", ""),
                explanation=result.get("explanation", ""),
                difficulty=request.difficulty.value,
                question_type=request.previous_question_type.value,
                chunks_used=len(chunks),
                processing_time=time.time() - start_time
            )
        else:
            return GeneratingAdditionalQuestionResponse(
                success=False,
                message="추가 문제 생성에 실패했습니다.",
                userId=request.userId,
                bookId=request.bookId,
                additional_question="",
                correct_answer="",
                explanation="",
                difficulty=request.difficulty.value,
                question_type=request.previous_question_type.value,
                chunks_used=len(chunks),
                processing_time=time.time() - start_time
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추가 문제 생성 중 오류가 발생했습니다: {str(e)}") 