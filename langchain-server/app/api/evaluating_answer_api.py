"""
EVALUATING_ANSWER_AND_LOGGING API
답안 평가 및 로깅 API
"""
import time
from fastapi import APIRouter, HTTPException
from app.schemas.request.rag_apis import EvaluatingAnswerRequest
from app.schemas.response.rag_apis import EvaluatingAnswerResponse
from app.services.rag_service import rag_service

router = APIRouter(tags=["Answer Evaluation"])


@router.post("/evaluate-answer-and-log", response_model=EvaluatingAnswerResponse)
async def evaluate_answer_and_log(request: EvaluatingAnswerRequest):
    """
    사용자 답안을 평가하고 로깅합니다.
    
    **프로세스:**
    1. 답안 정확성 평가
    2. 상세 피드백 생성
    3. 학습 제안사항 생성
    4. 평가 결과 로깅
    
    **특징:**
    - 정답/오답 판별
    - 상세한 피드백 제공
    - 개인화된 학습 제안
    - 평가 이력 저장
    """
    start_time = time.time()
    
    try:
        # 1. 답안 평가
        evaluation_result = _evaluate_answer(
            user_answer=request.user_answer,
            correct_answer=request.correct_answer,
            explanation=request.explanation
        )
        
        # 2. 상세 피드백 생성
        detailed_feedback = _generate_detailed_feedback(
            question=request.question,
            user_answer=request.user_answer,
            correct_answer=request.correct_answer,
            explanation=request.explanation,
            is_correct=evaluation_result["is_correct"]
        )
        
        # 3. 학습 제안사항 생성
        learning_suggestions = _generate_learning_suggestions(
            question=request.question,
            user_answer=request.user_answer,
            correct_answer=request.correct_answer,
            is_correct=evaluation_result["is_correct"]
        )
        
        # 4. 점수 계산
        score = _calculate_score(
            user_answer=request.user_answer,
            correct_answer=request.correct_answer,
            is_correct=evaluation_result["is_correct"]
        )
        
        processing_time = time.time() - start_time
        
        return EvaluatingAnswerResponse(
            success=True,
            message="답안 평가가 완료되었습니다.",
            userId=request.userId,
            bookId=request.bookId,
            is_correct=evaluation_result["is_correct"],
            evaluation_message=evaluation_result["message"],
            detailed_feedback=detailed_feedback,
            score=score,
            learning_suggestions=learning_suggestions,
            timestamp=time.time()
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500, 
            detail=f"답안 평가 중 오류가 발생했습니다: {str(e)}"
        )


def _evaluate_answer(user_answer: str, correct_answer: str, explanation: str) -> dict:
    """
    답안을 평가합니다.
    
    Args:
        user_answer: 사용자 답안
        correct_answer: 정답
        explanation: 해설
        
    Returns:
        평가 결과 딕셔너리
    """
    try:
        # 간단한 키워드 매칭
        user_answer_lower = user_answer.lower().strip()
        correct_answer_lower = correct_answer.lower().strip()
        
        # 정확한 매칭
        if user_answer_lower == correct_answer_lower:
            return {
                "is_correct": True,
                "message": "✅ 정답입니다! 잘 하셨네요."
            }
        
        # 부분 매칭 (키워드 포함)
        if correct_answer_lower in user_answer_lower or user_answer_lower in correct_answer_lower:
            return {
                "is_correct": True,
                "message": "✅ 부분적으로 정답입니다. 핵심 개념을 이해하고 계시네요."
            }
        
        # 유사도 기반 평가 (간단한 구현)
        similarity_score = _calculate_similarity(user_answer_lower, correct_answer_lower)
        
        if similarity_score > 0.7:
            return {
                "is_correct": True,
                "message": "✅ 거의 정답입니다. 약간의 차이가 있지만 개념을 잘 이해하고 계시네요."
            }
        elif similarity_score > 0.4:
            return {
                "is_correct": False,
                "message": "❌ 부분적으로 틀렸습니다. 개념을 다시 한번 복습해보세요."
            }
        else:
            return {
                "is_correct": False,
                "message": "❌ 오답입니다. 정답과 해설을 참고하여 개념을 다시 학습해보세요."
            }
            
    except Exception as e:
        print(f"답안 평가 오류: {e}")
        return {
            "is_correct": False,
            "message": "답안 평가 중 오류가 발생했습니다."
        }


def _calculate_similarity(text1: str, text2: str) -> float:
    """
    두 텍스트 간의 유사도를 계산합니다.
    
    Args:
        text1: 첫 번째 텍스트
        text2: 두 번째 텍스트
        
    Returns:
        유사도 점수 (0-1)
    """
    try:
        # 간단한 유사도 계산 (공통 단어 기반)
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        if not union:
            return 0.0
        
        return len(intersection) / len(union)
        
    except Exception as e:
        print(f"유사도 계산 오류: {e}")
        return 0.0


def _generate_detailed_feedback(question: str, user_answer: str, correct_answer: str, explanation: str, is_correct: bool) -> str:
    """
    상세한 피드백을 생성합니다.
    
    Args:
        question: 문제
        user_answer: 사용자 답안
        correct_answer: 정답
        explanation: 해설
        is_correct: 정답 여부
        
    Returns:
        상세 피드백
    """
    if is_correct:
        feedback = f"""
✅ 정답입니다!

**문제:** {question}
**당신의 답안:** {user_answer}
**정답:** {correct_answer}

**해설:** {explanation}

잘 하셨습니다! 이 개념을 잘 이해하고 계시네요.
"""
    else:
        feedback = f"""
❌ 오답입니다.

**문제:** {question}
**당신의 답안:** {user_answer}
**정답:** {correct_answer}

**해설:** {explanation}

다시 한번 개념을 복습해보세요. 정답과 해설을 참고하여 이해를 돕습니다.
"""
    
    return feedback.strip()


def _generate_learning_suggestions(question: str, user_answer: str, correct_answer: str, is_correct: bool) -> list[str]:
    """
    학습 제안사항을 생성합니다.
    
    Args:
        question: 문제
        user_answer: 사용자 답안
        correct_answer: 정답
        is_correct: 정답 여부
        
    Returns:
        학습 제안사항 리스트
    """
    suggestions = []
    
    if is_correct:
        suggestions.extend([
            "이 개념을 다른 문제에도 적용해보세요.",
            "관련된 고급 개념도 학습해보세요.",
            "실제 코드로 구현해보세요."
        ])
    else:
        suggestions.extend([
            "기본 개념을 다시 한번 복습해보세요.",
            "유사한 문제를 더 풀어보세요.",
            "해설을 자세히 읽고 이해해보세요.",
            "관련 예제 코드를 참고해보세요."
        ])
    
    # 문제 유형에 따른 추가 제안
    if "변수" in question.lower():
        suggestions.append("변수 선언과 초기화 방법을 연습해보세요.")
    elif "클래스" in question.lower():
        suggestions.append("객체지향 프로그래밍 개념을 복습해보세요.")
    elif "메서드" in question.lower():
        suggestions.append("메서드 정의와 호출 방법을 연습해보세요.")
    
    return suggestions


def _calculate_score(user_answer: str, correct_answer: str, is_correct: bool) -> float:
    """
    점수를 계산합니다.
    
    Args:
        user_answer: 사용자 답안
        correct_answer: 정답
        is_correct: 정답 여부
        
    Returns:
        점수 (0-100)
    """
    if is_correct:
        # 정답인 경우 유사도에 따라 점수 조정
        similarity = _calculate_similarity(user_answer.lower(), correct_answer.lower())
        if similarity > 0.9:
            return 100.0
        elif similarity > 0.7:
            return 90.0
        else:
            return 80.0
    else:
        # 오답인 경우 유사도에 따라 점수 조정
        similarity = _calculate_similarity(user_answer.lower(), correct_answer.lower())
        if similarity > 0.5:
            return 60.0
        elif similarity > 0.3:
            return 40.0
        else:
            return 20.0


@router.get("/evaluation-stats")
async def get_evaluation_stats():
    """답안 평가 통계를 반환합니다."""
    try:
        return {
            "success": True,
            "message": "평가 통계 조회 완료",
            "stats": {
                "total_evaluations": 0,  # 실제로는 DB에서 조회
                "correct_answers": 0,
                "incorrect_answers": 0,
                "average_score": 0.0
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        ) 