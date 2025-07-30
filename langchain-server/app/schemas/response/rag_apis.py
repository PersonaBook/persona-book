from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# 1. GENERATING_QUESTION_WITH_RAG
class GeneratingQuestionResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    userId: int = Field(..., description="사용자 ID")
    bookId: int = Field(..., description="책 ID")
    question: str = Field(..., description="생성된 문제")
    correct_answer: str = Field(..., description="정답")
    explanation: str = Field(..., description="해설")
    difficulty: str = Field(..., description="문제 난이도")
    question_type: str = Field(..., description="문제 유형")
    chunks_used: int = Field(..., description="사용된 청크 수")
    processing_time: float = Field(..., description="처리 시간 (초)")
    timestamp: datetime = Field(default_factory=datetime.now, description="생성 시간")


# 2. GENERATING_ADDITIONAL_QUESTION_WITH_RAG
class GeneratingAdditionalQuestionResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    userId: int = Field(..., description="사용자 ID")
    bookId: int = Field(..., description="책 ID")
    additional_question: str = Field(..., description="생성된 추가 문제")
    correct_answer: str = Field(..., description="정답")
    explanation: str = Field(..., description="해설")
    difficulty: str = Field(..., description="문제 난이도")
    question_type: str = Field(..., description="문제 유형")
    chunks_used: int = Field(..., description="사용된 청크 수")
    processing_time: float = Field(..., description="처리 시간 (초)")
    timestamp: datetime = Field(default_factory=datetime.now, description="생성 시간")


# 3. EVALUATING_ANSWER_AND_LOGGING
class EvaluatingAnswerResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    userId: int = Field(..., description="사용자 ID")
    bookId: int = Field(..., description="책 ID")
    is_correct: bool = Field(..., description="정답 여부")
    evaluation_message: str = Field(..., description="평가 메시지")
    detailed_feedback: str = Field(..., description="상세 피드백")
    score: Optional[float] = Field(None, description="점수 (0-100)")
    learning_suggestions: List[str] = Field(default_factory=list, description="학습 제안사항")
    timestamp: datetime = Field(default_factory=datetime.now, description="평가 시간")


# 4. PRESENTING_CONCEPT_EXPLANATION
class ConceptExplanationResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    userId: int = Field(..., description="사용자 ID")
    bookId: int = Field(..., description="책 ID")
    concept_name: str = Field(..., description="개념명")
    explanation: str = Field(..., description="개념 설명")
    examples: List[str] = Field(default_factory=list, description="예시")
    key_points: List[str] = Field(default_factory=list, description="핵심 포인트")
    related_concepts: List[str] = Field(default_factory=list, description="관련 개념")
    difficulty_level: str = Field(..., description="설명 난이도")
    chunks_used: int = Field(..., description="사용된 청크 수")
    processing_time: float = Field(..., description="처리 시간 (초)")
    timestamp: datetime = Field(default_factory=datetime.now, description="생성 시간")


# 5. REEXPLAINING_CONCEPT
class ReexplainingConceptResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    userId: int = Field(..., description="사용자 ID")
    bookId: int = Field(..., description="책 ID")
    concept_name: str = Field(..., description="개념명")
    reexplanation: str = Field(..., description="재설명")
    simplified_explanation: str = Field(..., description="단순화된 설명")
    visual_aids: List[str] = Field(default_factory=list, description="시각적 도구")
    step_by_step_guide: List[str] = Field(default_factory=list, description="단계별 가이드")
    common_misconceptions: List[str] = Field(default_factory=list, description="일반적인 오해")
    difficulty_level: str = Field(..., description="설명 난이도")
    chunks_used: int = Field(..., description="사용된 청크 수")
    processing_time: float = Field(..., description="처리 시간 (초)")
    timestamp: datetime = Field(default_factory=datetime.now, description="생성 시간")


# 6. PROCESSING_PAGE_SEARCH_RESULT
class PageSearchResponse(BaseModel):
    success: bool = Field(..., description="성공 여부")
    message: str = Field(..., description="응답 메시지")
    userId: int = Field(..., description="사용자 ID")
    bookId: int = Field(..., description="책 ID")
    search_keyword: str = Field(..., description="검색 키워드")
    search_results: List[Dict[str, Any]] = Field(..., description="검색 결과")
    total_results: int = Field(..., description="총 검색 결과 수")
    relevant_pages: List[int] = Field(default_factory=list, description="관련 페이지 번호")
    summary: str = Field(..., description="검색 결과 요약")
    search_type: str = Field(..., description="검색 유형")
    chunks_used: int = Field(..., description="사용된 청크 수")
    processing_time: float = Field(..., description="처리 시간 (초)")
    timestamp: datetime = Field(default_factory=datetime.now, description="검색 시간") 