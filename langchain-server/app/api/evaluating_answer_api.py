from fastapi import APIRouter, HTTPException
from app.schemas.request.rag_apis import EvaluatingAnswerRequest
from app.schemas.response.rag_apis import EvaluatingAnswerResponse
import time

router = APIRouter(tags=["Answer Evaluation"])


@router.post("/evaluating-answer", response_model=EvaluatingAnswerResponse)
async def evaluating_answer(request: EvaluatingAnswerRequest):
    """답안을 평가하고 결과를 로깅합니다."""
    start_time = time.time()
    
    try:
        # 간단한 키워드 기반 평가
        user_answer_lower = request.user_answer.lower()
        correct_answer_lower = request.correct_answer.lower()
        
        # 정답 키워드들
        correct_keywords = ["정답", "맞음", "correct", "right", "true", "맞다", "올바르다"]
        incorrect_keywords = ["오답", "틀림", "wrong", "false", "incorrect", "틀렸다", "잘못"]
        
        is_correct = any(keyword in user_answer_lower for keyword in correct_keywords)
        is_incorrect = any(keyword in user_answer_lower for keyword in incorrect_keywords)
        
        # 정답 여부 판단
        if is_correct:
            evaluation_result = True
            evaluation_message = "정답입니다!"
            detailed_feedback = "훌륭합니다! 정확한 답변을 하셨습니다."
            score = 100.0
        elif is_incorrect:
            evaluation_result = False
            evaluation_message = "오답입니다."
            detailed_feedback = f"정답은 '{request.correct_answer}'입니다. 다시 한번 확인해보세요."
            score = 0.0
        else:
            # 키워드가 없는 경우 정답과 비교
            if user_answer_lower in correct_answer_lower or correct_answer_lower in user_answer_lower:
                evaluation_result = True
                evaluation_message = "정답입니다!"
                detailed_feedback = "정확한 답변을 하셨습니다."
                score = 100.0
            else:
                evaluation_result = False
                evaluation_message = "오답입니다."
                detailed_feedback = f"정답은 '{request.correct_answer}'입니다. 설명을 다시 읽어보세요."
                score = 0.0
        
        # 학습 제안사항
        learning_suggestions = [
            "관련 개념을 다시 한번 복습해보세요.",
            "비슷한 문제를 더 풀어보세요.",
            "설명 부분을 자세히 읽어보세요."
        ]
        
        return EvaluatingAnswerResponse(
            success=True,
            message="답안 평가가 완료되었습니다.",
            userId=request.userId,
            bookId=request.bookId,
            is_correct=evaluation_result,
            evaluation_message=evaluation_message,
            detailed_feedback=detailed_feedback,
            score=score,
            learning_suggestions=learning_suggestions,
            processing_time=time.time() - start_time
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"답안 평가 중 오류가 발생했습니다: {str(e)}") 