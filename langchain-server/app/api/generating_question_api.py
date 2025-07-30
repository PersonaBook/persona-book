"""
GENERATING_QUESTION_WITH_RAG API
RAG를 사용한 문제 생성 API
"""
import time
from fastapi import APIRouter, HTTPException
# 예시: generating_question_api.py
from app.schemas.request.rag_apis import GeneratingQuestionRequest
from app.schemas.response.rag_apis import GeneratingQuestionResponse
from app.services.rag_service import rag_service

router = APIRouter(tags=["Question Generation"])


@router.post("/generate-question-with-rag", response_model=GeneratingQuestionResponse)
async def generate_question_with_rag(request: GeneratingQuestionRequest):
    """
    RAG를 사용하여 PDF 기반 문제를 생성합니다.
    
    **프로세스:**
    1. PDF 텍스트 추출 및 청킹
    2. Elasticsearch에 임베딩 저장
    3. 쿼리와 관련된 컨텍스트 검색
    4. RAG를 사용한 문제 생성
    
    **특징:**
    - 의미적 청킹으로 정확한 컨텍스트 제공
    - 난이도 및 문제 유형 선택 가능
    - 정답과 해설 포함
    """
    print(f"🎯 /generate-question-with-rag 엔드포인트 호출됨")
    print(f"📊 요청 데이터: userId={request.userId}, bookId={request.bookId}, query='{request.query}'")
    start_time = time.time()
    
    try:
        # 1. PDF 처리 및 RAG 설정
        success, message = rag_service.process_pdf_and_setup_rag(
            request.pdf_base64, 
            request.max_pages
        )
        
        if not success:
            return GeneratingQuestionResponse(
                success=False,
                message=message,
                userId=request.userId,
                bookId=request.bookId,
                question="",
                correct_answer="",
                explanation="",
                difficulty=request.difficulty.value,
                question_type=request.question_type.value,
                chunks_used=0,
                processing_time=time.time() - start_time
            )
        
        # 2. 관련 컨텍스트 검색
        relevant_chunks = rag_service.search_relevant_chunks(request.query, k=5)
        
        if not relevant_chunks:
            return GeneratingQuestionResponse(
                success=False,
                message="관련 컨텍스트를 찾을 수 없습니다.",
                userId=request.userId,
                bookId=request.bookId,
                question="",
                correct_answer="",
                explanation="",
                difficulty=request.difficulty.value,
                question_type=request.question_type.value,
                chunks_used=0,
                processing_time=time.time() - start_time
            )
        
        # 3. 컨텍스트 결합
        context = "\n\n".join([chunk.page_content for chunk in relevant_chunks])
        
        # 4. 문제 생성 프롬프트
        question_prompt = f"""
다음 Java 교재 내용을 바탕으로 {request.difficulty.value} 난이도의 {request.question_type.value} 문제를 생성해주세요.

**요청 내용:**
- 쿼리: {request.query}
- 난이도: {request.difficulty.value}
- 문제 유형: {request.question_type.value}

**교재 내용:**
{context}

**요구사항:**
1. Java 프로그래밍 관련 문제
2. 명확하고 이해하기 쉬운 문제
3. 정답과 함께 생성
4. 상세한 해설 포함
5. {request.difficulty.value} 난이도에 맞는 문제

**출력 형식:**
문제: [문제 내용]
정답: [정답]
해설: [상세한 해설]

위 형식으로 문제를 생성해주세요.
"""
        
        # 5. RAG를 사용한 문제 생성
        generated_content = rag_service.generate_rag_response(
            query=request.query,
            context=context,
            prompt_template=question_prompt
        )
        
        # 6. 응답 파싱 (간단한 파싱)
        question, correct_answer, explanation = _parse_generated_content(generated_content)
        
        processing_time = time.time() - start_time
        
        return GeneratingQuestionResponse(
            success=True,
            message="RAG를 사용한 문제 생성이 완료되었습니다.",
            userId=request.userId,
            bookId=request.bookId,
            question=question,
            correct_answer=correct_answer,
            explanation=explanation,
            difficulty=request.difficulty.value,
            question_type=request.question_type.value,
            chunks_used=len(relevant_chunks),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500, 
            detail=f"문제 생성 중 오류가 발생했습니다: {str(e)}"
        )


def _parse_generated_content(content: str) -> tuple[str, str, str]:
    """
    생성된 내용을 파싱하여 문제, 정답, 해설을 추출합니다.
    
    Args:
        content: 생성된 내용
        
    Returns:
        (문제, 정답, 해설)
    """
    try:
        lines = content.split('\n')
        question = ""
        correct_answer = ""
        explanation = ""
        
        current_section = ""
        
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
            else:
                if current_section == "question":
                    question += " " + line
                elif current_section == "answer":
                    correct_answer += " " + line
                elif current_section == "explanation":
                    explanation += " " + line
        
        # 기본값 설정
        if not question:
            question = content[:500] + "..." if len(content) > 500 else content
        if not correct_answer:
            correct_answer = "정답을 확인해주세요."
        if not explanation:
            explanation = "해설을 확인해주세요."
            
        return question.strip(), correct_answer.strip(), explanation.strip()
        
    except Exception as e:
        print(f"응답 파싱 오류: {e}")
        return content[:500], "정답을 확인해주세요.", "해설을 확인해주세요."


@router.get("/question-generation-stats")
async def get_question_generation_stats():
    """문제 생성 통계를 반환합니다."""
    try:
        stats = rag_service.get_processing_stats()
        return {
            "success": True,
            "message": "통계 조회 완료",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        ) 