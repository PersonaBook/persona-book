from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.repository.chat_history_repository import chat_history_repository
from app.schemas.response.chat_history import (
    ChatHistoryListResponse,
    ChatHistoryDetailResponse,
    ChatHistorySearchResponse,
    ChatHistoryDeleteResponse,
    ChatHistoryResponse
)

router = APIRouter(prefix="/chat-history", tags=["Chat History"])

@router.get("", response_model=ChatHistoryListResponse)
async def get_all_chat_history(
    size: int = Query(default=100, ge=1, le=1000, description="조회할 개수")
):
    """모든 채팅 이력을 조회합니다."""
    try:
        history_list = chat_history_repository.get_all_chat_history(size=size)
        response_list = [ChatHistoryResponse.from_entity(history) for history in history_list]
        
        return ChatHistoryListResponse(
            history=response_list,
            total_count=len(response_list)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 이력 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/{history_id}", response_model=ChatHistoryDetailResponse)
async def get_chat_history_by_id(history_id: str):
    """ID로 특정 채팅 이력을 조회합니다."""
    try:
        history = chat_history_repository.get_chat_history_by_id(history_id)
        if not history:
            raise HTTPException(status_code=404, detail="채팅 이력을 찾을 수 없습니다")
        
        return ChatHistoryDetailResponse(
            history=ChatHistoryResponse.from_entity(history)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 이력 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/search/", response_model=ChatHistorySearchResponse)
async def search_chat_history(
    query: str = Query(..., description="검색할 키워드"),
    size: int = Query(default=10, ge=1, le=100, description="검색 결과 개수")
):
    """채팅 이력을 검색합니다."""
    try:
        history_list = chat_history_repository.search_chat_history(query, size=size)
        response_list = [ChatHistoryResponse.from_entity(history) for history in history_list]
        
        return ChatHistorySearchResponse(
            history=response_list,
            total_count=len(response_list),
            query=query
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 이력 검색 중 오류가 발생했습니다: {str(e)}")

@router.get("/recent/", response_model=ChatHistoryListResponse)
async def get_recent_chat_history(
    days: int = Query(default=7, ge=1, le=365, description="최근 N일"),
    size: int = Query(default=50, ge=1, le=500, description="조회할 개수")
):
    """최근 N일 내의 채팅 이력을 조회합니다."""
    try:
        history_list = chat_history_repository.get_recent_chat_history(days=days, size=size)
        response_list = [ChatHistoryResponse.from_entity(history) for history in history_list]
        
        return ChatHistoryListResponse(
            history=response_list,
            total_count=len(response_list)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최근 채팅 이력 조회 중 오류가 발생했습니다: {str(e)}")

@router.get("/age-group/{age_group}", response_model=ChatHistoryListResponse)
async def get_chat_history_by_age_group(
    age_group: str,
    size: int = Query(default=50, ge=1, le=500, description="조회할 개수")
):
    """연령대별 채팅 이력을 조회합니다."""
    try:
        history_list = chat_history_repository.get_chat_history_by_age_group(age_group, size=size)
        response_list = [ChatHistoryResponse.from_entity(history) for history in history_list]
        
        return ChatHistoryListResponse(
            history=response_list,
            total_count=len(response_list)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"연령대별 채팅 이력 조회 중 오류가 발생했습니다: {str(e)}")

@router.delete("/{history_id}", response_model=ChatHistoryDeleteResponse)
async def delete_chat_history(history_id: str):
    """채팅 이력을 삭제합니다."""
    try:
        success = chat_history_repository.delete_chat_history(history_id)
        if not success:
            raise HTTPException(status_code=404, detail="삭제할 채팅 이력을 찾을 수 없습니다")
        
        return ChatHistoryDeleteResponse(
            message="채팅 이력이 성공적으로 삭제되었습니다",
            deleted_id=history_id
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"채팅 이력 삭제 중 오류가 발생했습니다: {str(e)}") 