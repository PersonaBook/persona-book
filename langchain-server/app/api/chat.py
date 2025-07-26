from app.schemas.request.chat import FeatureContext, StageContext, UserMessageRequest
from app.schemas.response.chat import AiMessageResponse
from fastapi import APIRouter

router = APIRouter()


@router.post("/chat", response_model=AiMessageResponse)
def chat(user: UserMessageRequest):
    match user.stageContext:
        # 1. 초기 진입
        case StageContext.START:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content="안녕하세요! 무엇을 도와드릴까요?\n1. 예상 문제 생성\n2. 페이지 찾기\n3. 개념 설명",
                featureContext=FeatureContext.INITIAL,
                stageContext=StageContext.SELECT_TYPE,
            )

        # 2. 기능 선택
        case StageContext.SELECT_TYPE:
            match user.content:
                case "1":  # 예상 문제 생성 선택
                    return AiMessageResponse(
                        userId=user.userId,
                        bookId=user.bookId,
                        content="문제를 어떤 기준으로 생성할까요?\n1. 챕터/페이지 범위\n2. 특정 개념",
                        featureContext=FeatureContext.PROBLEM_GENERATION,
                        stageContext=StageContext.SELECT_PROBLEM_TYPE,
                    )
                case "2":  # 페이지 찾기 (향후 확장)
                    return AiMessageResponse(
                        userId=user.userId,
                        bookId=user.bookId,
                        content="찾고 싶은 개념이나 키워드를 입력해주세요.\n예: 프로세스와 스레드 차이",
                        featureContext=FeatureContext.INITIAL,
                        stageContext=StageContext.PROMPT_CHAPTER_PAGE,
                    )
                case "3":  # 개념 설명
                    return AiMessageResponse(
                        userId=user.userId,
                        bookId=user.bookId,
                        content="설명을 듣고 싶은 개념을 입력해주세요.\n예: 다형성, HTTP, 세션/쿠키",
                        featureContext=FeatureContext.CONCEPT_EXPLANATION,
                        stageContext=StageContext.EXPLANATION_PRESENTED,
                    )
                case _:
                    return AiMessageResponse(
                        userId=user.userId,
                        bookId=user.bookId,
                        content="잘못된 입력입니다. 1, 2 또는 3을 입력해주세요.",
                        featureContext=user.featureContext,
                        stageContext=user.stageContext,
                    )

        # 문제 생성 기준 선택
        case StageContext.SELECT_PROBLEM_TYPE:
            match user.content:
                case "1":
                    return AiMessageResponse(
                        userId=user.userId,
                        bookId=user.bookId,
                        content="챕터나 페이지 범위를 입력해주세요.\n예: 챕터 3 또는 150-160페이지",
                        featureContext=FeatureContext.PROBLEM_GENERATION,
                        stageContext=StageContext.PROMPT_CHAPTER_PAGE,
                    )
                case "2":
                    return AiMessageResponse(
                        userId=user.userId,
                        bookId=user.bookId,
                        content="어떤 개념에 대한 문제를 원하시나요?\n예: OOP, DB, 네트워크 등",
                        featureContext=FeatureContext.PROBLEM_GENERATION,
                        stageContext=StageContext.PROMPT_CONCEPT,
                    )
                case _:
                    return AiMessageResponse(
                        userId=user.userId,
                        bookId=user.bookId,
                        content="잘못된 입력입니다. 1 또는 2를 입력해주세요.",
                        featureContext=user.featureContext,
                        stageContext=user.stageContext,
                    )

        # 챕터/페이지 입력 → 문제 생성
        case StageContext.PROMPT_CHAPTER_PAGE:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content=f"[문제] {user.content}에 대한 예상 문제입니다:\n\nQ. 다형성이란 무엇인가요?",
                featureContext=FeatureContext.PROBLEM_SOLVING,
                stageContext=StageContext.PROBLEM_PRESENTED,
            )

        # 개념 입력 → 문제 생성
        case StageContext.PROMPT_CONCEPT:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content=f"[문제] '{user.content}'에 대한 질문입니다:\n\nQ. {user.content}의 핵심 개념을 설명해보세요.",
                featureContext=FeatureContext.PROBLEM_SOLVING,
                stageContext=StageContext.PROBLEM_PRESENTED,
            )

        # 문제 제시 → 정답 피드백
        case StageContext.PROBLEM_PRESENTED:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content="정답입니다! 다음 문제를 풀어보시겠습니까?\n1. 네\n2. 아니오",
                featureContext=FeatureContext.PROBLEM_SOLVING,
                stageContext=StageContext.CORRECT_FEEDBACK,
            )

        # 정답 이후 피드백
        case StageContext.CORRECT_FEEDBACK:
            if user.content == "1":
                return AiMessageResponse(
                    userId=user.userId,
                    bookId=user.bookId,
                    content="[문제] 다형성의 예시를 설명해보세요.",
                    featureContext=FeatureContext.PROBLEM_SOLVING,
                    stageContext=StageContext.PROBLEM_PRESENTED,
                )
            else:
                return AiMessageResponse(
                    userId=user.userId,
                    bookId=user.bookId,
                    content="다음에 무엇을 하시겠어요?\n1. 문제 생성\n2. 개념 설명",
                    featureContext=FeatureContext.INITIAL,
                    stageContext=StageContext.PROMPT_NEXT_ACTION,
                )

        # 다음 기능 제안
        case StageContext.PROMPT_NEXT_ACTION:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content="다음 기능을 선택해주세요.\n1. 문제 생성\n2. 개념 설명",
                featureContext=FeatureContext.INITIAL,
                stageContext=StageContext.SELECT_TYPE,
            )

        # 개념 설명 요청
        case StageContext.EXPLANATION_PRESENTED:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content=f"{user.content}에 대한 설명입니다.\n\n이해가 되셨나요? 1~5점으로 평가해주세요.",
                featureContext=FeatureContext.CONCEPT_EXPLANATION,
                stageContext=StageContext.FEEDBACK_RATING,
            )

        # 별점 평가
        case StageContext.FEEDBACK_RATING:
            try:
                score = int(user.content)
                if score >= 4:
                    return AiMessageResponse(
                        userId=user.userId,
                        bookId=user.bookId,
                        content="좋습니다! 다음 기능을 선택해주세요.\n1. 문제 생성\n2. 개념 설명",
                        featureContext=FeatureContext.INITIAL,
                        stageContext=StageContext.SELECT_TYPE,
                    )
                else:
                    return AiMessageResponse(
                        userId=user.userId,
                        bookId=user.bookId,
                        content="어떤 점이 이해되지 않았는지 설명해주세요.",
                        featureContext=FeatureContext.CONCEPT_EXPLANATION,
                        stageContext=StageContext.PROMPT_FEEDBACK_TEXT,
                    )
            except ValueError:
                return AiMessageResponse(
                    userId=user.userId,
                    bookId=user.bookId,
                    content="1~5 사이의 숫자로 입력해주세요.",
                    featureContext=FeatureContext.CONCEPT_EXPLANATION,
                    stageContext=StageContext.FEEDBACK_RATING,
                )

        # 사용자 피드백 → 재설명
        case StageContext.PROMPT_FEEDBACK_TEXT:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content="감사합니다. 피드백을 반영하여 다시 설명드릴게요.",
                featureContext=FeatureContext.CONCEPT_EXPLANATION,
                stageContext=StageContext.RE_EXPLANATION_PRESENTED,
            )

        # 재설명 → 다시 평가
        case StageContext.RE_EXPLANATION_PRESENTED:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content="다시 설명드렸습니다. 이제 얼마나 이해가 되셨나요? 1~5점으로 평가해주세요.",
                featureContext=FeatureContext.CONCEPT_EXPLANATION,
                stageContext=StageContext.FEEDBACK_RATING,
            )

        # 디폴트 fallback
        case _:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content=f"[DEBUG] 정의되지 않은 단계입니다. 입력: {user.content}",
                featureContext=user.featureContext,
                stageContext=user.stageContext,
            )
