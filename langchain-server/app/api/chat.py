from app.schemas.request.chat import UserMessageRequest
from app.schemas.response.chat import AiMessageResponse
from app.schemas.enum import ChatState
from app.services.question_generator_service import question_generator_service
from app.services.pdf_service import pdf_service
from app.services.openai_service import openai_service
from fastapi import APIRouter, HTTPException
import base64
import tempfile
import os

router = APIRouter()

# 전역 변수로 현재 문제의 정답 정보 저장
current_question_answer = {}


@router.get("/ping")
def ping():
    return {"status": "ok"}


@router.post("/chat", response_model=AiMessageResponse)
def chat(user: UserMessageRequest):
    """채팅 상태에 따른 AI 응답 생성"""
    print(f"🎯 /chat 엔드포인트 호출됨 - 이 메시지가 보이면 chat.py가 호출된 것입니다!")
    print(f"📊 요청 데이터: userId={user.userId}, bookId={user.bookId}, content='{user.content}', chatState={user.chatState}")
    print(f"🔍 ChatState 값: {user.chatState}")
    print(f"🔍 ChatState 타입: {type(user.chatState)}")
    print(f"🔍 ChatState 문자열: {str(user.chatState)}")
    print(f"🔍 ChatState == GENERATING_QUESTION_WITH_RAG: {user.chatState == ChatState.GENERATING_QUESTION_WITH_RAG}")
    try:
        match user.chatState:
            # ───────────── 예상 문제 생성 흐름 ─────────────
            case ChatState.GENERATING_QUESTION_WITH_RAG:
                print(f"🎯 GENERATING_QUESTION_WITH_RAG 매칭됨")
                return _handle_generating_question(user)
                
            case ChatState.GENERATING_ADDITIONAL_QUESTION:
                print(f"🎯 GENERATING_ADDITIONAL_QUESTION 매칭됨")
                return _handle_generating_additional_question(user)
                
            case ChatState.EVALUATING_ANSWER_AND_LOGGING:
                print(f"🎯 EVALUATING_ANSWER_AND_LOGGING 매칭됨")
                return _handle_evaluating_answer_and_logging(user)
                
            case ChatState.REEXPLAINING_CONCEPT:
                print(f"🎯 REEXPLAINING_CONCEPT 매칭됨")
                return _handle_reexplaining_concept(user)
                
            # ───────────── 개념 설명 흐름 ─────────────
            case ChatState.PRESENTING_CONCEPT_EXPLANATION:
                print(f"🎯 PRESENTING_CONCEPT_EXPLANATION 매칭됨")
                return _handle_presenting_concept_explanation(user)
                
            # ───────────── 페이지 찾기 흐름 ─────────────
            case ChatState.WAITING_KEYWORD_FOR_PAGE_SEARCH:
                print(f"🎯 WAITING_KEYWORD_FOR_PAGE_SEARCH 매칭됨")
                return _handle_waiting_keyword_for_page_search(user)
                
            case ChatState.PROCESSING_PAGE_SEARCH_RESULT:
                print(f"🎯 PROCESSING_PAGE_SEARCH_RESULT 매칭됨")
                return _handle_processing_page_search_result(user)
                
            # 기타 처리되지 않은 상태
            case _:
                print(f"❌ 처리되지 않은 ChatState: {user.chatState}")
                return AiMessageResponse(
                    userId=user.userId,
                    bookId=user.bookId,
                    content="죄송합니다. 아직 처리되지 않은 상태입니다.",
                    messageType="TEXT",
                    sender="AI",
                    chatState=user.chatState,
                )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 처리 중 오류가 발생했습니다: {str(e)}")


def _handle_generating_question(user: UserMessageRequest) -> AiMessageResponse:
    """RAG와 로컬 임베딩을 모두 사용한 문제 생성 처리"""
    global current_question_answer
    try:
        print(f"🚀 _handle_generating_question 시작")
        print(f"🔍 question_generator_service 사용")
        # 사용자 메시지를 쿼리로 사용
        query = user.content if user.content else "Java 프로그래밍"
        print(f"📝 쿼리: {query}")
        
        # PDF 처리 및 청킹 (pdf_service 사용)
        pdf_path = "/app/javajungsuk4_sample.pdf"
        if os.path.exists(pdf_path):
            print(f"📄 PDF 파일 처리 중: {pdf_path}")
            chunks = pdf_service().process_pdf_and_create_chunks(pdf_path, max_pages=20)
            print(f"✅ PDF 처리 완료: {len(chunks) if chunks else 0}개 청크")
        else:
            print(f"❌ PDF 파일을 찾을 수 없음: {pdf_path}")
            chunks = None
        
        if chunks:
            # 벡터 스토어 설정
            print(f"🔧 벡터 스토어 설정 중...")
            success = question_generator_service.setup_vector_store(chunks)
            print(f"✅ 벡터 스토어 설정: {'성공' if success else '실패'}")
            
            if success:
                # 문제 생성
                print(f"🎯 문제 생성 중...")
                result = question_generator_service.generate_question_with_rag(
                    query=query,
                    difficulty="보통",
                    question_type="객관식"
                )
                print(f"✅ 문제 생성 완료: {result.get('success', False)}")
                
                if result.get("success", False):
                    # 문제와 정답 정보를 함께 저장
                    question = result.get("question", "문제가 생성되었습니다.")
                    answer = result.get("correct_answer", "")
                    explanation = result.get("explanation", "")
                    options = result.get("options", [])
                    
                    # 디버깅 로그 추가
                    print(f"🔍 문제: {question}")
                    print(f"🔍 선택지: {options}")
                    print(f"🔍 선택지 개수: {len(options) if options else 0}")
                    
                    # 문제 텍스트 생성 (정답 정보는 제외)
                    if options and len(options) > 0:
                        # 객관식인 경우 선택지 포함
                        content = f"{question}\n\n"
                        for i, option in enumerate(options, 1):
                            content += f"{i}. {option}\n"
                        print(f"✅ 선택지 포함된 문제 생성 완료")
                    else:
                        # 주관식인 경우 문제만
                        content = f"{question}"
                        print(f"⚠️ 선택지가 없어 주관식으로 생성됨")
                    
                    # 정답 정보를 세션에 저장
                    current_question_answer = {
                        "answer": answer,
                        "explanation": explanation
                    }
                else:
                    content = result.get("message", "문제 생성에 실패했습니다.")
                    print(f"❌ 문제 생성 실패: {content}")
            else:
                content = "문서 설정에 실패했습니다."
                print(f"❌ 벡터 스토어 설정 실패")
        else:
            content = "PDF 처리에 실패했습니다."
            print(f"❌ PDF 처리 실패")
        
        # 최종 응답에서 정답 정보 제거
        import re
        final_content = re.sub(r'\[정답 정보:.*?\]', '', content, flags=re.DOTALL).strip()
        final_content = re.sub(r'정답 정보:.*?$', '', final_content, flags=re.DOTALL).strip()
        final_content = re.sub(r'\[정답.*?\]', '', final_content, flags=re.DOTALL).strip()
        final_content = re.sub(r'정답.*?$', '', final_content, flags=re.DOTALL).strip()
        print(f"🔍 최종 응답 content: {final_content}")
        
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=final_content,
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
        )
    except Exception as e:
        print(f"❌ 문제 생성 중 오류: {str(e)}")
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=f"문제 생성 중 오류가 발생했습니다: {str(e)}",
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
        )


def _handle_generating_additional_question(user: UserMessageRequest) -> AiMessageResponse:
    """추가 문제 생성 처리"""
    try:
        # 기존 문제와 유사한 추가 문제 생성
        query = user.content if user.content else "Java 프로그래밍"
        
        # 추가 문제 생성 (기존과 다른 유형)
        result = question_generator_service.generate_question_with_rag(
            query=query,
            difficulty="보통",
            question_type="주관식"  # 다른 유형으로 생성
        )
        
        # 결과가 딕셔너리인 경우 처리
        if isinstance(result, dict):
            if result.get("success", False):
                content = result.get("question", "추가 문제가 생성되었습니다.")
            else:
                content = result.get("message", "추가 문제 생성에 실패했습니다.")
        else:
            # 문자열인 경우 그대로 사용
            content = str(result)
        
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=content,
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
        )
    except Exception as e:
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=f"추가 문제 생성 중 오류가 발생했습니다: {str(e)}",
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
        )


def _handle_evaluating_answer_and_logging(user: UserMessageRequest) -> AiMessageResponse:
    """답안 평가 및 로깅 처리"""
    try:
        user_answer = user.content.lower()
        
        # 간단한 키워드 기반 평가 (실제로는 더 정교한 로직 필요)
        correct_keywords = ["정답", "맞음", "correct", "right", "true", "맞다", "올바르다"]
        incorrect_keywords = ["오답", "틀림", "wrong", "false", "incorrect", "틀렸다", "잘못"]
        
        is_correct = any(keyword in user_answer for keyword in correct_keywords)
        is_incorrect = any(keyword in user_answer for keyword in incorrect_keywords)
        
        if is_correct:
            response_content = "✅ 정답입니다! 잘 하셨네요. 이 개념을 잘 이해하고 계시는군요."
        elif is_incorrect:
            response_content = "❌ 오답입니다. 다시 한번 개념을 복습해보세요."
        else:
            # 정답/오답 판별이 어려운 경우 - 사용자에게 직접 물어보기
            response_content = "답안을 평가하기 위해 정답 여부를 알려주세요. 답에 '정답' 또는 '오답'을 포함해서 입력해주세요."
        
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=response_content,
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
        )
    except Exception as e:
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=f"답안 평가 중 오류가 발생했습니다: {str(e)}",
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
        )


def _handle_presenting_concept_explanation(user: UserMessageRequest) -> AiMessageResponse:
    """개념 설명 처리"""
    try:
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
            chatState=user.chatState,
        )
    except Exception as e:
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=f"개념 설명 중 오류가 발생했습니다: {str(e)}",
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
        )


def _handle_reexplaining_concept(user: UserMessageRequest) -> AiMessageResponse:
    """개념 재설명 처리"""
    try:
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
            chatState=user.chatState,
        )
    except Exception as e:
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=f"개념 재설명 중 오류가 발생했습니다: {str(e)}",
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
        )


def _handle_waiting_keyword_for_page_search(user: UserMessageRequest) -> AiMessageResponse:
    """페이지 검색 키워드 대기 처리"""
    try:
        keyword = user.content if user.content else ""
        
        if not keyword:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content="검색하고 싶은 키워드를 입력해주세요.",
                messageType="TEXT",
                sender="AI",
                chatState=user.chatState,
            )
        
        # 페이지 검색 로직 (실제 구현 필요)
        search_result = f"'{keyword}'에 대한 검색 결과를 찾았습니다."
        
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=search_result,
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
        )
    except Exception as e:
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=f"페이지 검색 중 오류가 발생했습니다: {str(e)}",
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
        )


def _handle_processing_page_search_result(user: UserMessageRequest) -> AiMessageResponse:
    """페이지 검색 결과 처리"""
    try:
        # 검색 결과 처리 로직
        search_query = user.content if user.content else ""
        
        if not search_query:
            return AiMessageResponse(
                userId=user.userId,
                bookId=user.bookId,
                content="검색할 내용을 입력해주세요.",
                messageType="TEXT",
                sender="AI",
                chatState=user.chatState,
            )
        
        # 실제 검색 결과 처리 (벡터 스토어 활용)
        if question_generator_service.vector_store:
            docs = question_generator_service.vector_store.similarity_search(search_query, k=3)
            if docs:
                result_content = f"'{search_query}'에 대한 관련 내용을 찾았습니다:\n\n"
                for i, doc in enumerate(docs, 1):
                    result_content += f"{i}. {doc.page_content[:200]}...\n\n"
            else:
                result_content = f"'{search_query}'에 대한 관련 내용을 찾지 못했습니다."
        else:
            result_content = "검색 서비스를 사용할 수 없습니다."
        
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=result_content,
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
        )
    except Exception as e:
        return AiMessageResponse(
            userId=user.userId,
            bookId=user.bookId,
            content=f"검색 결과 처리 중 오류가 발생했습니다: {str(e)}",
            messageType="TEXT",
            sender="AI",
            chatState=user.chatState,
        )

def _parse_generated_content(content: str) -> tuple[str, str, str]:
    """
    생성된 콘텐츠에서 문제, 정답, 해설을 파싱합니다.
    
    Args:
        content: 생성된 콘텐츠
        
    Returns:
        (문제, 정답, 해설) 튜플
    """
    try:
        lines = content.strip().split('\n')
        question = ""
        correct_answer = ""
        explanation = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("문제:"):
                current_section = "question"
                question = line.replace("문제:", "").strip()
            elif line.startswith("정답:"):
                current_section = "answer"
                correct_answer = line.replace("정답:", "").strip()
            elif line.startswith("해설:"):
                current_section = "explanation"
                explanation = line.replace("해설:", "").strip()
            elif current_section == "question":
                question += " " + line
            elif current_section == "answer":
                correct_answer += " " + line
            elif current_section == "explanation":
                explanation += " " + line
        
        # 기본값 설정
        if not question:
            question = "문제가 생성되었습니다."
        if not correct_answer:
            correct_answer = "정답을 확인할 수 없습니다."
        if not explanation:
            explanation = "해설을 확인할 수 없습니다."
        
        return question.strip(), correct_answer.strip(), explanation.strip()
        
    except Exception as e:
        print(f"콘텐츠 파싱 중 오류: {e}")
        return "문제가 생성되었습니다.", "정답을 확인할 수 없습니다.", "해설을 확인할 수 없습니다."

