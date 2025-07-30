"""
GENERATING_ADDITIONAL_QUESTION_WITH_RAG API
로컬 임베딩을 사용한 추가 문제 생성 API
"""
import time
import base64
import tempfile
import os
from fastapi import APIRouter, HTTPException
from app.schemas.request.rag_apis import GeneratingAdditionalQuestionRequest
from app.schemas.response.rag_apis import GeneratingAdditionalQuestionResponse
from app.services.local_pdf_service import get_local_pdf_service
from app.services.enhanced_local_question_generator import get_enhanced_local_question_generator_service

router = APIRouter(tags=["Additional Question Generation"])


@router.post("/generate-additional-question-with-rag", response_model=GeneratingAdditionalQuestionResponse)
async def generate_additional_question_with_rag(request: GeneratingAdditionalQuestionRequest):
    """
    로컬 임베딩을 사용하여 추가 문제를 생성합니다.
    
    **프로세스:**
    1. PDF 텍스트 추출 및 청킹
    2. 로컬 임베딩을 사용한 유사도 검색
    3. 이전 문제와 다른 유형의 문제 생성
    4. 챕터별 맞춤형 문제 템플릿 활용
    
    **특징:**
    - OpenAI API 할당량에 의존하지 않음
    - 이전 문제와 다른 유형으로 생성
    - 동일한 개념에 대한 다양한 관점
    - 학습 효과 극대화
    """
    start_time = time.time()
    temp_file_path = None
    
    try:
        # 1. Base64 문자열을 PDF 파일로 디코딩하여 임시 파일로 저장
        try:
            pdf_data = base64.b64decode(request.pdf_base64)
            print(f"📄 디코딩된 PDF 데이터 크기: {len(pdf_data)} bytes")
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_data)
                temp_file_path = temp_file.name
                print(f"📁 임시 PDF 파일 생성: {temp_file_path}")
                
            # 파일이 제대로 생성되었는지 확인
            import os
            if os.path.exists(temp_file_path):
                file_size = os.path.getsize(temp_file_path)
                print(f"📊 임시 파일 크기: {file_size} bytes")
            else:
                print("❌ 임시 파일 생성 실패")
                return GeneratingAdditionalQuestionResponse(
                    success=False,
                    message="PDF 파일 생성에 실패했습니다.",
                    userId=request.userId,
                    bookId=request.bookId,
                    additional_question="",
                    correct_answer="",
                    explanation="",
                    difficulty=request.difficulty.value,
                    question_type=request.previous_question_type.value,
                    chunks_used=0,
                    processing_time=time.time() - start_time
                )
        except Exception as e:
            print(f"❌ Base64 디코딩 오류: {e}")
            return GeneratingAdditionalQuestionResponse(
                success=False,
                message=f"PDF 디코딩에 실패했습니다: {str(e)}",
                userId=request.userId,
                bookId=request.bookId,
                additional_question="",
                correct_answer="",
                explanation="",
                difficulty=request.difficulty.value,
                question_type=request.previous_question_type.value,
                chunks_used=0,
                processing_time=time.time() - start_time
            )

        # 2. PDF 처리 및 청킹
        local_pdf_service = get_local_pdf_service()
        # max_pages가 None이거나 5보다 작으면 20으로 설정
        effective_max_pages = request.max_pages if request.max_pages and request.max_pages >= 5 else 20
        print(f"📄 PDF 처리: 최대 {effective_max_pages}페이지")
        
        chunks = local_pdf_service.process_pdf_and_create_chunks(
            temp_file_path,
            max_pages=effective_max_pages
        )

        if not chunks:
            return GeneratingAdditionalQuestionResponse(
                success=False,
                message="PDF 처리에 실패했습니다.",
                userId=request.userId,
                bookId=request.bookId,
                additional_question="",
                correct_answer="",
                explanation="",
                difficulty=request.difficulty.value,
                question_type=request.previous_question_type.value,
                chunks_used=0,
                processing_time=time.time() - start_time
            )

        # 3. 향상된 로컬 문제 생성 서비스 설정
        enhanced_question_service = get_enhanced_local_question_generator_service()
        success = enhanced_question_service.setup_documents(chunks)
        if not success:
            return GeneratingAdditionalQuestionResponse(
                success=False,
                message="문서 설정에 실패했습니다.",
                userId=request.userId,
                bookId=request.bookId,
                additional_question="",
                correct_answer="",
                explanation="",
                difficulty=request.difficulty.value,
                question_type=request.previous_question_type.value,
                chunks_used=len(chunks),
                processing_time=time.time() - start_time
            )

        # 4. 추가 문제 생성 (이전과 다른 유형)
        result = enhanced_question_service.generate_question_with_rag(
            request.query,
            request.difficulty.value,
            request.previous_question_type.value
        )
        
        if result["success"]:
            # 문제 텍스트 생성
            question_text = f"문제: {result['question']}\n정답: {result['answer']}\n해설: {result['explanation']}"
            
            processing_time = time.time() - start_time
            
            return GeneratingAdditionalQuestionResponse(
                success=True,
                message="로컬 임베딩을 사용한 추가 문제 생성이 완료되었습니다.",
                userId=request.userId,
                bookId=request.bookId,
                additional_question=result['question'],
                correct_answer=result['answer'],
                explanation=result['explanation'],
                difficulty=request.difficulty.value,
                question_type=request.previous_question_type.value,
                chunks_used=result.get('context_used', len(chunks)),
                processing_time=processing_time
            )
        else:
            return GeneratingAdditionalQuestionResponse(
                success=False,
                message=result["message"],
                userId=request.userId,
                bookId=request.bookId,
                additional_question="",
                correct_answer="",
                explanation="",
                difficulty=request.difficulty.value,
                question_type=request.previous_question_type.value,
                chunks_used=len(chunks),
                processing_time=time.time() - start_time
            )
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500, 
            detail=f"추가 문제 생성 중 오류가 발생했습니다: {str(e)}"
        )
    finally:
        # 임시 파일 삭제
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


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


@router.get("/additional-question-stats")
async def get_additional_question_stats():
    """추가 문제 생성 통계를 반환합니다."""
    try:
        enhanced_question_service = get_enhanced_local_question_generator_service()
        stats = {
            "total_keywords": len(enhanced_question_service.keywords_data),
            "chapters": enhanced_question_service.chapter_pages,
            "service_type": "local_embedding",
            "openai_dependency": False
        }
        return {
            "success": True,
            "message": "로컬 임베딩 통계 조회 완료",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        ) 