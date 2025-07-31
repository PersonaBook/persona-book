"""
통합 채팅 API - Spring Boot ChatService에서 호출하는 /chat 엔드포인트
"""
from app.schemas.request.chat import UserMessageRequest
from app.schemas.response.chat import AiMessageResponse, GeneratingQuestionResponse
from app.schemas.enum import ChatState
from fastapi import APIRouter, HTTPException

# 다른 API들에서 함수 import
from app.api.question_generation_api import handle_generating_question, handle_generating_additional_question
from app.api.answer_evaluation_api import handle_evaluating_answer_and_logging
from app.api.concept_explanation_api import handle_presenting_concept_explanation, handle_reexplaining_concept
from app.api.page_search_new_api import handle_processing_page_search_result

router = APIRouter()

@router.post("/chat")
def unified_chat_handler(user: UserMessageRequest):
    """
    ChatState에 따라 적절한 핸들러로 라우팅하는 통합 엔드포인트
    """
    try:
        print("=" * 50)
        print(f"🚀🚀🚀 UNIFIED CHAT API 호출됨!!! 🚀🚀🚀")
        print(f"📊 ChatState: {user.chatState}")
        print(f"📊 요청 데이터: userId={user.userId}, bookId={user.bookId}, content='{user.content}'")
        print("=" * 50)
        
        # ChatState에 따라 적절한 핸들러 호출
        if user.chatState == ChatState.GENERATING_QUESTION_WITH_RAG:
            return handle_generating_question(user)
        elif user.chatState == ChatState.GENERATING_ADDITIONAL_QUESTION_WITH_RAG:
            return handle_generating_additional_question(user)
        elif user.chatState == ChatState.EVALUATING_ANSWER_AND_LOGGING:
            return handle_evaluating_answer_and_logging(user)
        elif user.chatState == ChatState.PRESENTING_CONCEPT_EXPLANATION:
            return handle_presenting_concept_explanation(user)
        elif user.chatState == ChatState.REEXPLAINING_CONCEPT:
            return handle_reexplaining_concept(user)
        elif user.chatState == ChatState.PROCESSING_PAGE_SEARCH_RESULT:
            return handle_processing_page_search_result(user)
        else:
            # 지원하지 않는 상태의 경우 기본 응답
            print(f"⚠️ 지원하지 않는 ChatState: {user.chatState}")
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content=f"현재 상태 '{user.chatState}'는 처리할 수 없습니다.",
                messageType="TEXT",
                sender="AI",
                chatState=user.chatState,
            )
            
    except Exception as e:
        print(f"❌ 통합 채팅 API 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"채팅 처리 중 오류가 발생했습니다: {str(e)}")