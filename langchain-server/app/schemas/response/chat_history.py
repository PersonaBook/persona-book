from datetime import datetime
from typing import List, Optional

from app.entity.chat_history import ChatHistory
from pydantic import BaseModel


class ChatHistoryResponse(BaseModel):
    """API 응답용 ChatHistory 래퍼"""

    id: Optional[str] = None
    age: int
    background: str
    feedback: str
    question: str
    answer: str
    created_at: Optional[datetime] = None
    model_name: str
    difficulty_level: str
    age_group: str

    @classmethod
    def from_entity(cls, entity: ChatHistory) -> "ChatHistoryResponse":
        """엔티티에서 API 응답 모델 생성"""
        return cls(
            id=entity.id,
            age=entity.age,
            background=entity.background,
            feedback=entity.feedback,
            question=entity.question,
            answer=entity.answer,
            created_at=entity.created_at,
            model_name=entity.model_name,
            difficulty_level=entity.get_difficulty_level(),
            age_group=entity.get_age_group(),
        )


class ChatHistoryListResponse(BaseModel):
    """채팅 이력 목록 조회 API 응답"""

    history: List[ChatHistoryResponse]
    total_count: int


class ChatHistoryDetailResponse(BaseModel):
    """채팅 이력 상세 조회 API 응답"""

    history: ChatHistoryResponse


class ChatHistorySearchResponse(BaseModel):
    """채팅 이력 검색 API 응답"""

    history: List[ChatHistoryResponse]
    total_count: int
    query: str


class ChatHistoryDeleteResponse(BaseModel):
    """채팅 이력 삭제 API 응답"""

    message: str
    deleted_id: str
