"""
PROCESSING_PAGE_SEARCH_RESULT API
페이지 검색 결과 처리 API
"""
import time
from fastapi import APIRouter, HTTPException
from app.schemas.request.rag_apis import PageSearchRequest
from app.schemas.response.rag_apis import PageSearchResponse
from app.services.rag_service import rag_service

router = APIRouter(tags=["Page Search"])


@router.post("/process-page-search-result", response_model=PageSearchResponse)
async def process_page_search_result(request: PageSearchRequest):
    """
    RAG를 사용하여 페이지 검색 결과를 처리합니다.
    
    **프로세스:**
    1. PDF 텍스트 추출 및 청킹
    2. Elasticsearch에 임베딩 저장
    3. 키워드 기반 검색
    4. 검색 결과 요약 및 정리
    
    **특징:**
    - 키워드 기반 정확한 검색
    - 검색 유형별 결과 분류
    - 관련 페이지 번호 제공
    - 검색 결과 요약
    """
    start_time = time.time()
    
    try:
        # 1. PDF 처리 및 RAG 설정
        success, message = rag_service.process_pdf_and_setup_rag(
            request.pdf_base64, 
            request.max_pages
        )
        
        if not success:
            return PageSearchResponse(
                success=False,
                message=message,
                userId=request.userId,
                bookId=request.bookId,
                search_keyword=request.search_keyword,
                search_results=[],
                total_results=0,
                relevant_pages=[],
                summary="",
                search_type=request.search_type,
                chunks_used=0,
                processing_time=time.time() - start_time
            )
        
        # 2. 키워드 기반 검색
        search_query = _build_search_query(request.search_keyword, request.search_type)
        relevant_chunks = rag_service.search_relevant_chunks(search_query, k=request.max_results)
        
        if not relevant_chunks:
            return PageSearchResponse(
                success=False,
                message=f"'{request.search_keyword}'에 대한 검색 결과를 찾을 수 없습니다.",
                userId=request.userId,
                bookId=request.bookId,
                search_keyword=request.search_keyword,
                search_results=[],
                total_results=0,
                relevant_pages=[],
                summary="",
                search_type=request.search_type,
                chunks_used=0,
                processing_time=time.time() - start_time
            )
        
        # 3. 검색 결과 처리
        search_results = _process_search_results(relevant_chunks, request.search_type)
        relevant_pages = _extract_relevant_pages(relevant_chunks)
        
        # 4. 검색 결과 요약 생성
        summary_prompt = f"""
다음 검색 결과를 바탕으로 '{request.search_keyword}'에 대한 요약을 생성해주세요.

**검색 키워드:** {request.search_keyword}
**검색 유형:** {request.search_type}

**검색 결과:**
{chr(10).join([f"- {result['content'][:200]}..." for result in search_results])}

**요구사항:**
1. 핵심 내용 요약
2. 주요 포인트 정리
3. 관련 페이지 정보 포함
4. {request.search_type} 유형에 맞는 요약

위 형식으로 요약해주세요.
"""
        
        summary = rag_service.generate_rag_response(
            query=request.search_keyword,
            context="\n\n".join([chunk.page_content for chunk in relevant_chunks]),
            prompt_template=summary_prompt
        )
        
        processing_time = time.time() - start_time
        
        return PageSearchResponse(
            success=True,
            message=f"'{request.search_keyword}'에 대한 검색이 완료되었습니다.",
            userId=request.userId,
            bookId=request.bookId,
            search_keyword=request.search_keyword,
            search_results=search_results,
            total_results=len(search_results),
            relevant_pages=relevant_pages,
            summary=summary,
            search_type=request.search_type,
            chunks_used=len(relevant_chunks),
            processing_time=processing_time
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        raise HTTPException(
            status_code=500, 
            detail=f"페이지 검색 중 오류가 발생했습니다: {str(e)}"
        )


def _build_search_query(keyword: str, search_type: str) -> str:
    """
    검색 쿼리를 구성합니다.
    
    Args:
        keyword: 검색 키워드
        search_type: 검색 유형
        
    Returns:
        구성된 검색 쿼리
    """
    if search_type == "concept":
        return f"{keyword} 개념 정의 설명"
    elif search_type == "example":
        return f"{keyword} 예시 코드 샘플"
    elif search_type == "definition":
        return f"{keyword} 정의 설명"
    else:
        return keyword


def _process_search_results(chunks, search_type: str) -> list[dict]:
    """
    검색 결과를 처리합니다.
    
    Args:
        chunks: 검색된 청크들
        search_type: 검색 유형
        
    Returns:
        처리된 검색 결과 리스트
    """
    results = []
    
    for i, chunk in enumerate(chunks, 1):
        # 청크에서 페이지 번호 추출
        page_number = chunk.metadata.get('page_number', 0)
        
        # 검색 유형에 따른 결과 분류
        result_type = _classify_search_result(chunk.page_content, search_type)
        
        result = {
            "id": i,
            "content": chunk.page_content,
            "page_number": page_number,
            "result_type": result_type,
            "relevance_score": 1.0 - (i * 0.1),  # 간단한 관련도 점수
            "word_count": len(chunk.page_content.split())
        }
        
        results.append(result)
    
    return results


def _classify_search_result(content: str, search_type: str) -> str:
    """
    검색 결과를 분류합니다.
    
    Args:
        content: 검색 결과 내용
        search_type: 검색 유형
        
    Returns:
        분류된 결과 유형
    """
    content_lower = content.lower()
    
    if search_type == "concept":
        if "정의" in content_lower or "개념" in content_lower:
            return "concept_definition"
        elif "설명" in content_lower or "이해" in content_lower:
            return "concept_explanation"
        else:
            return "concept_general"
    
    elif search_type == "example":
        if "예제" in content_lower or "예시" in content_lower:
            return "code_example"
        elif "코드" in content_lower or "실행" in content_lower:
            return "code_sample"
        else:
            return "example_general"
    
    elif search_type == "definition":
        if "정의" in content_lower:
            return "formal_definition"
        elif "개념" in content_lower:
            return "concept_definition"
        else:
            return "definition_general"
    
    else:
        return "general"


def _extract_relevant_pages(chunks) -> list[int]:
    """
    관련 페이지 번호를 추출합니다.
    
    Args:
        chunks: 검색된 청크들
        
    Returns:
        관련 페이지 번호 리스트
    """
    pages = set()
    
    for chunk in chunks:
        page_number = chunk.metadata.get('page_number', 0)
        if page_number > 0:
            pages.add(page_number)
    
    return sorted(list(pages))


@router.get("/page-search-stats")
async def get_page_search_stats():
    """페이지 검색 통계를 반환합니다."""
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