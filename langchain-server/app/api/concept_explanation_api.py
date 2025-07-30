"""
개념 설명 관련 API
"""
from app.schemas.request.chat import UserMessageRequest
from app.schemas.response.chat import AiMessageResponse
from app.schemas.enum import ChatState
from app.services.openai_service import openai_service
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/presenting-concept-explanation", response_model=AiMessageResponse)
def handle_presenting_concept_explanation(user: UserMessageRequest):
    """개념 설명 처리"""
    try:
        print(f"🚀 개념 설명 API 호출됨")
        print(f"📊 설명할 개념: {user.content}")
        
        concept_query = user.content if user.content else "Java 기본 개념"
        
        # OpenAI 서비스를 사용한 개념 설명
        from app.schemas.request.openai_chat import OpenAIChatRequest
        
        openai_request = OpenAIChatRequest(
            age=25,  # 기본값
            background="학습자",
            feedback="",
            question=f"{concept_query}에 대해 자세히 설명해주세요."
        )
        
        explanation = openai_service.ask_openai(openai_request)
        
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=explanation,
            messageType="TEXT",
            sender="AI",
            chatState=ChatState.PRESENTING_CONCEPT_EXPLANATION,
        )
    except Exception as e:
        print(f"❌ 개념 설명 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"개념 설명 중 오류가 발생했습니다: {str(e)}")


@router.post("/reexplaining-concept", response_model=AiMessageResponse)
def handle_reexplaining_concept(user: UserMessageRequest):
    """개념 재설명 처리"""
    try:
        print(f"🚀 개념 재설명 API 호출됨")
        print(f"📊 사용자 피드백: {user.content}")
        
        # 사용자의 피드백을 바탕으로 재설명
        feedback = user.content if user.content else "이해가 안 됩니다"
        
        from app.schemas.request.openai_chat import OpenAIChatRequest
        
        openai_request = OpenAIChatRequest(
            age=25,
            background="학습자",
            feedback=feedback,
            question="이전 설명이 이해되지 않았습니다. 더 쉽게 다시 설명해주세요."
        )
        
        reexplanation = openai_service.ask_openai(openai_request)
        
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=reexplanation,
            messageType="TEXT",
            sender="AI",
            chatState=ChatState.REEXPLAINING_CONCEPT,
        )
    except Exception as e:
        print(f"❌ 개념 재설명 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"개념 재설명 중 오류가 발생했습니다: {str(e)}")