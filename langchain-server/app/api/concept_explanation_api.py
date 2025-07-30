from fastapi import APIRouter, HTTPException
from app.schemas.request.rag_apis import ConceptExplanationRequest
from app.schemas.response.rag_apis import ConceptExplanationResponse
from app.services.openai_service import openai_service
from app.schemas.request.openai_chat import OpenAIChatRequest
import time

router = APIRouter(tags=["Concept Explanation"])


@router.post("/concept-explanation", response_model=ConceptExplanationResponse)
async def concept_explanation(request: ConceptExplanationRequest):
    """개념에 대한 설명을 생성합니다."""
    start_time = time.time()
    
    try:
        # OpenAI 서비스를 사용하여 개념 설명 생성
        openai_request = OpenAIChatRequest(
            age=25,  # 기본값
            background="학습자",
            feedback="",
            question=f"{request.concept_query}에 대해 자세히 설명해주세요."
        )
        
        explanation = openai_service.ask_openai(openai_request)
        
        # 예시, 핵심 포인트, 관련 개념 추출 (간단한 구현)
        examples = [
            f"{request.concept_query}의 예시 1",
            f"{request.concept_query}의 예시 2"
        ]
        
        key_points = [
            f"{request.concept_query}의 핵심 포인트 1",
            f"{request.concept_query}의 핵심 포인트 2"
        ]
        
        related_concepts = [
            f"{request.concept_query}와 관련된 개념 1",
            f"{request.concept_query}와 관련된 개념 2"
        ]
        
        return ConceptExplanationResponse(
            success=True,
            message="개념 설명이 완료되었습니다.",
            userId=request.userId,
            bookId=request.bookId,
            concept_name=request.concept_query,
            explanation=explanation,
            examples=examples,
            key_points=key_points,
            related_concepts=related_concepts,
            difficulty_level=request.user_level.value,
            chunks_used=0,  # 실제 구현에서는 청크 수 계산
            processing_time=time.time() - start_time
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"개념 설명 중 오류가 발생했습니다: {str(e)}") 