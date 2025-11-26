"""
답안 평가 관련 API
"""
from fastapi import APIRouter, HTTPException
from app.schemas.request.rag_apis import AnswerEvaluationRequest
from app.schemas.response.rag_apis import AnswerEvaluationResponse
from app.core.logging_config import get_logger
import re

logger = get_logger(__name__)

router = APIRouter()

# 전역 변수로 현재 문제의 정답 정보 가져오기
def get_current_question_answer():
    """question_generation_api에서 저장된 정답 정보 가져오기"""
    try:
        from app.api.question_generation_api import current_question_answer
        return current_question_answer
    except ImportError:
        return {}

def normalize_answer(answer: str) -> str:
    """답안 정규화 (공백 제거, 소문자 변환 등)"""
    if not answer:
        return ""
    return re.sub(r'\s+', '', str(answer).lower().strip())

def compare_answers(user_answer: str, correct_answer: str) -> bool:
    """사용자 답안과 정답 비교"""
    user_normalized = normalize_answer(user_answer)
    correct_normalized = normalize_answer(correct_answer)
    
    logger.debug(f"답안 비교: 사용자='{user_normalized}' vs 정답='{correct_normalized}'")
    
    # 정확한 일치
    if user_normalized == correct_normalized:
        return True
    
    # 숫자 답안의 경우 (예: "3", "③", "3번")
    user_num = re.findall(r'\d+', user_answer)
    correct_num = re.findall(r'\d+', correct_answer)
    
    if user_num and correct_num:
        return user_num[0] == correct_num[0]
    
    # 선택지 형태 비교 (예: "A", "a", "1번", "①")
    # 사용자 답안에서 특수 선택지 변환
    user_converted = user_answer
    if '①' in user_answer:
        user_converted = '1'
    elif '②' in user_answer:
        user_converted = '2'
    elif '③' in user_answer:
        user_converted = '3'
    elif '④' in user_answer:
        user_converted = '4'
    elif '⑤' in user_answer:
        user_converted = '5'
    elif 'ⓐ' in user_answer.lower():
        user_converted = '1'
    elif 'ⓑ' in user_answer.lower():
        user_converted = '2'
    elif 'ⓒ' in user_answer.lower():
        user_converted = '3'
    elif 'ⓓ' in user_answer.lower():
        user_converted = '4'
    elif 'ⓔ' in user_answer.lower():
        user_converted = '5'
    
    # 변환된 답안 비교
    if normalize_answer(user_converted) == normalize_answer(correct_answer):
        return True
    
    # A, B, C, D, E 형태 처리
    if len(user_answer.strip()) == 1 and user_answer.strip().lower() in 'abcde':
        user_num = str(ord(user_answer.strip().lower()) - ord('a') + 1)
        if user_num == correct_answer.strip():
            return True
    
    return False

@router.post("/evaluating/answer", response_model=AnswerEvaluationResponse)
def handle_evaluating_answer_and_logging(request: AnswerEvaluationRequest):
    """답안 평가 및 로깅 처리"""
    try:
        logger.info("답안 평가 API 호출됨")
        logger.debug(f"사용자 답안: '{request.user_answer}'")
        
        # 저장된 정답 정보 가져오기
        question_data = get_current_question_answer()
        logger.debug(f"저장된 정답 정보: {question_data}")
        
        if not question_data or "answer" not in question_data:
            logger.warning("정답 정보가 없습니다.")
            response_content = "죄송합니다. 문제의 정답 정보를 찾을 수 없습니다. 다시 문제를 생성해주세요."
            is_correct = False
        else:
            correct_answer = question_data.get("answer", "")
            explanation = question_data.get("explanation", "")
            user_answer = request.user_answer.strip()
            
            logger.debug(f"정답: '{correct_answer}'")
            logger.debug(f"사용자 답안: '{user_answer}'")
            
            # 답안 비교
            is_correct = compare_answers(user_answer, correct_answer)
            
            if is_correct:
                response_content = f"정답입니다! 잘 하셨네요!\n\n"
                if explanation:
                    response_content += f"**해설:**\n{explanation}"
                else:
                    response_content += "이 개념을 잘 이해하고 계시는군요."
                logger.info("정답 처리 완료")
            else:
                response_content = f"오답입니다.\n\n"
                response_content += f"**정답:** {correct_answer}\n\n"
                if explanation:
                    response_content += f"**해설:**\n{explanation}\n\n"
                response_content += "다시 한번 개념을 복습해보세요."
                logger.info("오답 처리 완료")
        
        return AnswerEvaluationResponse(
            is_correct=is_correct,
            feedback=response_content,
            correct_answer=question_data.get("answer", "") if question_data else ""
        )
    except Exception as e:
        logger.error(f"답안 평가 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"답안 평가 중 오류가 발생했습니다: {str(e)}")
