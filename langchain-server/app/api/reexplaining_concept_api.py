"""
REEXPLAINING_CONCEPT API
개념 재설명 API
"""
import time
from fastapi import APIRouter, HTTPException
from app.schemas.request.rag_apis import ReexplainingConceptRequest
from app.schemas.response.rag_apis import ReexplainingConceptResponse
from app.services.rag_service import rag_service

router = APIRouter(tags=["Concept Reexplanation"])


@router.post("/reexplain-concept", response_model=ReexplainingConceptResponse)
async def reexplain_concept(request: ReexplainingConceptRequest):
    """
    RAG를 사용하여 개념을 재설명합니다.
    
    **프로세스:**
    1. PDF 텍스트 추출 및 청킹
    2. Elasticsearch에 임베딩 저장
    3. 사용자 피드백을 바탕으로 재설명
    4. RAG를 사용한 개념 재설명 생성
    
    **특징:**
    - 사용자 피드백 반영
    - 더 쉬운 설명 제공
    - 단계별 가이드 포함
    - 일반적인 오해 해소
    """
    start_time = time.time()
    
    try:
        # 1. PDF 처리 및 RAG 설정
        success, message = rag_service.process_pdf_and_setup_rag(
            request.pdf_base64, 
            request.max_pages
        )
        
        if not success:
            return ReexplainingConceptResponse(
                success=False,
                message=message,
                userId=request.userId,
                bookId=request.bookId,
                concept_name=request.original_concept,
                reexplanation="",
                simplified_explanation="",
                visual_aids=[],
                step_by_step_guide=[],
                common_misconceptions=[],
                difficulty_level=request.difficulty_level,
                chunks_used=0,
                processing_time=time.time() - start_time
            )
        
        # 2. 관련 컨텍스트 검색
        relevant_chunks = rag_service.search_relevant_chunks(request.original_concept, k=7)
        
        if not relevant_chunks:
            return ReexplainingConceptResponse(
                success=False,
                message="관련 컨텍스트를 찾을 수 없습니다.",
                userId=request.userId,
                bookId=request.bookId,
                concept_name=request.original_concept,
                reexplanation="",
                simplified_explanation="",
                visual_aids=[],
                step_by_step_guide=[],
                common_misconceptions=[],
                difficulty_level=request.difficulty_level,
                chunks_used=0,
                processing_time=time.time() - start_time
            )
        
        # 3. 컨텍스트 결합
        context = "\n\n".join([chunk.page_content for chunk in relevant_chunks])
        
        # 4. 개념 재설명 프롬프트
        reexplanation_prompt = f"""
다음 Java 교재 내용을 바탕으로 '{request.original_concept}'에 대한 개념을 재설명해주세요.

**요청 내용:**
- 원래 개념: {request.original_concept}
- 사용자 피드백: {request.user_feedback}
- 설명 난이도: {request.difficulty_level}

**교재 내용:**
{context}

**요구사항:**
1. 사용자 피드백을 반영한 {request.difficulty_level} 설명
2. 더 쉽고 이해하기 쉬운 설명
3. 단계별 가이드 제공
4. 일반적인 오해 해소
5. 시각적 도구 제안
6. 실제 예시 포함

**출력 형식:**
개념명: [개념명]
재설명: [사용자 피드백을 반영한 상세한 재설명]
단순화된설명: [매우 간단한 설명]
단계별가이드: [단계별 학습 가이드]
일반적오해: [일반적인 오해들]
시각도구: [이해를 돕는 시각적 도구들]

위 형식으로 개념을 재설명해주세요.
"""
        
        # 5. RAG를 사용한 개념 재설명 생성
        generated_content = rag_service.generate_rag_response(
            query=request.original_concept,
            context=context,
            prompt_template=reexplanation_prompt
        )
        
        # 6. 응답 파싱
        parsed_content = _parse_reexplanation(generated_content, request.original_concept)
        
        processing_time = time.time() - start_time
        
        return ReexplainingConceptResponse(
            success=True,
            message="개념 재설명이 완료되었습니다.",
            userId=request.userId,
            bookId=request.bookId,
            concept_name=parsed_content["concept_name"],
            reexplanation=parsed_content["reexplanation"],
            simplified_explanation=parsed_content["simplified_explanation"],
            visual_aids=parsed_content["visual_aids"],
            step_by_step_guide=parsed_content["step_by_step_guide"],
            common_misconceptions=parsed_content["common_misconceptions"],
            difficulty_level=request.difficulty_level,
            chunks_used=len(relevant_chunks),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500, 
            detail=f"개념 재설명 중 오류가 발생했습니다: {str(e)}"
        )


def _parse_reexplanation(content: str, original_concept: str) -> dict:
    """
    생성된 개념 재설명을 파싱합니다.
    
    Args:
        content: 생성된 내용
        original_concept: 원래 개념
        
    Returns:
        파싱된 내용 딕셔너리
    """
    try:
        lines = content.split('\n')
        concept_name = original_concept
        reexplanation = ""
        simplified_explanation = ""
        visual_aids = []
        step_by_step_guide = []
        common_misconceptions = []
        
        current_section = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("개념명:"):
                current_section = "concept_name"
                concept_name = line.replace("개념명:", "").strip()
            elif line.startswith("재설명:"):
                current_section = "reexplanation"
                reexplanation = line.replace("재설명:", "").strip()
            elif line.startswith("단순화된설명:"):
                current_section = "simplified_explanation"
                simplified_explanation = line.replace("단순화된설명:", "").strip()
            elif line.startswith("단계별가이드:"):
                current_section = "step_by_step_guide"
                step = line.replace("단계별가이드:", "").strip()
                if step:
                    step_by_step_guide.append(step)
            elif line.startswith("일반적오해:"):
                current_section = "common_misconceptions"
                misconception = line.replace("일반적오해:", "").strip()
                if misconception:
                    common_misconceptions.append(misconception)
            elif line.startswith("시각도구:"):
                current_section = "visual_aids"
                visual_aid = line.replace("시각도구:", "").strip()
                if visual_aid:
                    visual_aids.append(visual_aid)
            else:
                if current_section == "reexplanation":
                    reexplanation += " " + line
                elif current_section == "simplified_explanation":
                    simplified_explanation += " " + line
                elif current_section == "step_by_step_guide":
                    if line.startswith("-") or line.startswith("*"):
                        step = line[1:].strip()
                        if step:
                            step_by_step_guide.append(step)
                    else:
                        step_by_step_guide.append(line)
                elif current_section == "common_misconceptions":
                    if line.startswith("-") or line.startswith("*"):
                        misconception = line[1:].strip()
                        if misconception:
                            common_misconceptions.append(misconception)
                    else:
                        common_misconceptions.append(line)
                elif current_section == "visual_aids":
                    if line.startswith("-") or line.startswith("*"):
                        visual_aid = line[1:].strip()
                        if visual_aid:
                            visual_aids.append(visual_aid)
                    else:
                        visual_aids.append(line)
        
        # 기본값 설정
        if not reexplanation:
            reexplanation = content[:1000] + "..." if len(content) > 1000 else content
        if not simplified_explanation:
            simplified_explanation = "간단한 설명을 확인해주세요."
        if not step_by_step_guide:
            step_by_step_guide = ["단계별 가이드를 확인해주세요."]
        if not common_misconceptions:
            common_misconceptions = ["일반적인 오해를 확인해주세요."]
        if not visual_aids:
            visual_aids = ["시각적 도구를 확인해주세요."]
            
        return {
            "concept_name": concept_name,
            "reexplanation": reexplanation.strip(),
            "simplified_explanation": simplified_explanation.strip(),
            "visual_aids": visual_aids,
            "step_by_step_guide": step_by_step_guide,
            "common_misconceptions": common_misconceptions
        }
        
    except Exception as e:
        print(f"개념 재설명 파싱 오류: {e}")
        return {
            "concept_name": original_concept,
            "reexplanation": content[:1000] + "..." if len(content) > 1000 else content,
            "simplified_explanation": "간단한 설명을 확인해주세요.",
            "visual_aids": ["시각적 도구를 확인해주세요."],
            "step_by_step_guide": ["단계별 가이드를 확인해주세요."],
            "common_misconceptions": ["일반적인 오해를 확인해주세요."]
        }


@router.get("/reexplanation-stats")
async def get_reexplanation_stats():
    """개념 재설명 통계를 반환합니다."""
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