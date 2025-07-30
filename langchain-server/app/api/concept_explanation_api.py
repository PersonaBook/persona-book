"""
PRESENTING_CONCEPT_EXPLANATION API
개념 설명 API
"""
import time
from fastapi import APIRouter, HTTPException
from app.schemas.request.rag_apis import ConceptExplanationRequest
from app.schemas.response.rag_apis import ConceptExplanationResponse
from app.services.rag_service import rag_service

router = APIRouter(tags=["Concept Explanation"])


@router.post("/present-concept-explanation", response_model=ConceptExplanationResponse)
async def present_concept_explanation(request: ConceptExplanationRequest):
    """
    RAG를 사용하여 개념을 설명합니다.
    
    **프로세스:**
    1. PDF 텍스트 추출 및 청킹
    2. Elasticsearch에 임베딩 저장
    3. 개념과 관련된 컨텍스트 검색
    4. RAG를 사용한 개념 설명 생성
    
    **특징:**
    - 사용자 수준에 맞는 설명
    - 예시와 핵심 포인트 포함
    - 관련 개념 연결
    - 시각적 도구 제안
    """
    start_time = time.time()
    
    try:
        # 1. PDF 처리 및 RAG 설정
        success, message = rag_service.process_pdf_and_setup_rag(
            request.pdf_base64, 
            request.max_pages
        )
        
        if not success:
            return ConceptExplanationResponse(
                success=False,
                message=message,
                userId=request.userId,
                bookId=request.bookId,
                concept_name=request.concept_query,
                explanation="",
                examples=[],
                key_points=[],
                related_concepts=[],
                difficulty_level=request.user_level,
                chunks_used=0,
                processing_time=time.time() - start_time
            )
        
        # 2. 관련 컨텍스트 검색
        relevant_chunks = rag_service.search_relevant_chunks(request.concept_query, k=7)
        
        if not relevant_chunks:
            return ConceptExplanationResponse(
                success=False,
                message="관련 컨텍스트를 찾을 수 없습니다.",
                userId=request.userId,
                bookId=request.bookId,
                concept_name=request.concept_query,
                explanation="",
                examples=[],
                key_points=[],
                related_concepts=[],
                difficulty_level=request.user_level,
                chunks_used=0,
                processing_time=time.time() - start_time
            )
        
        # 3. 컨텍스트 결합
        context = "\n\n".join([chunk.page_content for chunk in relevant_chunks])
        
        # 4. 개념 설명 프롬프트
        concept_explanation_prompt = f"""
다음 Java 교재 내용을 바탕으로 '{request.concept_query}'에 대한 개념을 설명해주세요.

**요청 내용:**
- 개념: {request.concept_query}
- 사용자 수준: {request.user_level}

**교재 내용:**
{context}

**요구사항:**
1. {request.user_level} 수준에 맞는 설명
2. 명확하고 이해하기 쉬운 설명
3. 실제 예시 포함
4. 핵심 포인트 정리
5. 관련 개념 연결
6. 시각적 도구 제안

**출력 형식:**
개념명: [개념명]
설명: [상세한 개념 설명]
예시: [실제 코드 예시]
핵심포인트: [주요 포인트들]
관련개념: [관련된 다른 개념들]
시각도구: [이해를 돕는 시각적 도구들]

위 형식으로 개념을 설명해주세요.
"""
        
        # 5. RAG를 사용한 개념 설명 생성
        generated_content = rag_service.generate_rag_response(
            query=request.concept_query,
            context=context,
            prompt_template=concept_explanation_prompt
        )
        
        # 6. 응답 파싱
        parsed_content = _parse_concept_explanation(generated_content, request.concept_query)
        
        processing_time = time.time() - start_time
        
        return ConceptExplanationResponse(
            success=True,
            message="개념 설명이 완료되었습니다.",
            userId=request.userId,
            bookId=request.bookId,
            concept_name=parsed_content["concept_name"],
            explanation=parsed_content["explanation"],
            examples=parsed_content["examples"],
            key_points=parsed_content["key_points"],
            related_concepts=parsed_content["related_concepts"],
            difficulty_level=request.user_level,
            chunks_used=len(relevant_chunks),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500, 
            detail=f"개념 설명 중 오류가 발생했습니다: {str(e)}"
        )


def _parse_concept_explanation(content: str, concept_query: str) -> dict:
    """
    생성된 개념 설명을 파싱합니다.
    
    Args:
        content: 생성된 내용
        concept_query: 원본 쿼리
        
    Returns:
        파싱된 내용 딕셔너리
    """
    try:
        lines = content.split('\n')
        concept_name = concept_query
        explanation = ""
        examples = []
        key_points = []
        related_concepts = []
        visual_aids = []
        
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("개념명:"):
                current_section = "concept_name"
                concept_name = line.replace("개념명:", "").strip()
            elif line.startswith("설명:"):
                current_section = "explanation"
                explanation = line.replace("설명:", "").strip()
            elif line.startswith("예시:"):
                current_section = "examples"
                example = line.replace("예시:", "").strip()
                if example:
                    examples.append(example)
            elif line.startswith("핵심포인트:"):
                current_section = "key_points"
                key_point = line.replace("핵심포인트:", "").strip()
                if key_point:
                    key_points.append(key_point)
            elif line.startswith("관련개념:"):
                current_section = "related_concepts"
                related_concept = line.replace("관련개념:", "").strip()
                if related_concept:
                    related_concepts.append(related_concept)
            elif line.startswith("시각도구:"):
                current_section = "visual_aids"
                visual_aid = line.replace("시각도구:", "").strip()
                if visual_aid:
                    visual_aids.append(visual_aid)
            else:
                if current_section == "explanation":
                    explanation += " " + line
                elif current_section == "examples":
                    if line.startswith("-") or line.startswith("*"):
                        example = line[1:].strip()
                        if example:
                            examples.append(example)
                    else:
                        examples.append(line)
                elif current_section == "key_points":
                    if line.startswith("-") or line.startswith("*"):
                        key_point = line[1:].strip()
                        if key_point:
                            key_points.append(key_point)
                    else:
                        key_points.append(line)
                elif current_section == "related_concepts":
                    if line.startswith("-") or line.startswith("*"):
                        related_concept = line[1:].strip()
                        if related_concept:
                            related_concepts.append(related_concept)
                    else:
                        related_concepts.append(line)
                elif current_section == "visual_aids":
                    if line.startswith("-") or line.startswith("*"):
                        visual_aid = line[1:].strip()
                        if visual_aid:
                            visual_aids.append(visual_aid)
                    else:
                        visual_aids.append(line)
        
        # 기본값 설정
        if not explanation:
            explanation = content[:1000] + "..." if len(content) > 1000 else content
        if not examples:
            examples = ["예시를 확인해주세요."]
        if not key_points:
            key_points = ["핵심 포인트를 확인해주세요."]
        if not related_concepts:
            related_concepts = ["관련 개념을 확인해주세요."]
            
        return {
            "concept_name": concept_name,
            "explanation": explanation.strip(),
            "examples": examples,
            "key_points": key_points,
            "related_concepts": related_concepts,
            "visual_aids": visual_aids
        }
        
    except Exception as e:
        print(f"개념 설명 파싱 오류: {e}")
        return {
            "concept_name": concept_query,
            "explanation": content[:1000] + "..." if len(content) > 1000 else content,
            "examples": ["예시를 확인해주세요."],
            "key_points": ["핵심 포인트를 확인해주세요."],
            "related_concepts": ["관련 개념을 확인해주세요."],
            "visual_aids": []
        }


@router.get("/concept-explanation-stats")
async def get_concept_explanation_stats():
    """개념 설명 통계를 반환합니다."""
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