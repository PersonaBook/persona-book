from fastapi import APIRouter
from app.schemas.chat import UserMessageDto, AiMessageDto, ChatState

router = APIRouter()

@router.get("/ping")
def ping():
    return {"status": "ok"}


@router.post("/chat", response_model=AiMessageDto)
def chat(user: UserMessageDto):
    # FastAPI는 chatState에 따라 메시지 응답만 생성하며, 상태 전이는 Spring에서 수행됨
    match user.chatState:
        # ───────────── 예상 문제 생성 흐름 ─────────────
        case ChatState.GENERATING_QUESTION_WITH_RAG:
            # 사용자가 선택한 기준에 따라 예상 문제 생성
            return AiMessageDto(
                userId=user.userId,
                bookId=user.bookId,
                content="(생성한 예상 문제)",
                messageType="TEXT",
                sender="AI",
                chatState=user.chatState
            )

        case ChatState.GENERATING_ADDITIONAL_QUESTION_WITH_RAG:
            # 추가 예상 문제 생성 로직
            # 문제를 풀고 <문제 더 풀기> 선택지를 선택한 경우, 기존에 선택한 문제 유형에 해당하는 추가 예상 문제 생성
            return AiMessageDto(
                userId=user.userId,
                bookId=user.bookId,
                content="(생성한 추가 예상 문제)",
                messageType="TEXT",
                sender="AI",
                chatState=user.chatState
            )

        case ChatState.EVALUATING_ANSWER_AND_LOGGING:
            # 정답 여부 판단 및 해설
            # + 추가 기능(오답 기록)
            if "정답" in user.content:
                return AiMessageDto(
                    userId=user.userId,
                    bookId=user.bookId,
                    content="정답 (정답 여부 판별)",
                    messageType="TEXT",
                    sender="AI",
                    chatState=user.chatState
                )
            else:
                return AiMessageDto(
                    userId=user.userId,
                    bookId=user.bookId,
                    content="오답 (정답 여부 판별)",
                    messageType="TEXT",
                    sender="AI",
                    chatState=user.chatState
                )

        case ChatState.REEXPLAINING_CONCEPT:
            # 사용자로 부터 해설에 대한 평가를 낮게한 이유를 받아
            # 이를 바탕으로 이전에 설명한 개념을 보충 설명
            return AiMessageDto(
                userId=user.userId,
                bookId=user.bookId,
                content="(재설명)",
                messageType="TEXT",
                sender="AI",
                chatState=user.chatState
            )


        # ───────────── 개념 설명 흐름 ─────────────
        case ChatState.PRESENTING_CONCEPT_EXPLANATION:
            # 사용자가 요청한 개념에 대한 설명
            return AiMessageDto(
                userId=user.userId,
                bookId=user.bookId,
                content="(개념 설명)",
                messageType="TEXT",
                sender="AI",
                chatState=user.chatState
            )


        # ───────────── 페이지 찾기 흐름 ─────────────
        case ChatState.WAITING_KEYWORD_FOR_PAGE_SEARCH:
            return AiMessageDto(
                userId=user.userId,
                bookId=user.bookId,
                content="(페이지 찾기)",
                messageType="TEXT",
                sender="AI",
                chatState=user.chatState
            )


        # 기타 처리되지 않은 상태
        case _:
            return AiMessageDto(
                userId=user.userId,
                bookId=user.bookId,
                content="죄송합니다. 아직 처리되지 않은 상태입니다.",
                messageType="TEXT",
                sender="AI",
                chatState=user.chatState
            )