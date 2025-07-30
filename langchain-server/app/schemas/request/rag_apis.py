# app/schemas/request/rag_apis.py

from enum import Enum
from typing import Optional
from pydantic import BaseModel


class DifficultyLevel(str, Enum):
    """문제/설명 난이도"""
    EASY = "쉬움"
    NORMAL = "보통"
    HARD = "어려움"


class QuestionType(str, Enum):
    """문제 유형"""
    MULTIPLE_CHOICE = "객관식"
    SHORT_ANSWER = "주관식"


class SearchType(str, Enum):
    """검색 유형"""
    KEYWORD = "keyword"
    FULL_TEXT = "full_text"
    # 필요에 따라 더 추가


class GeneratingQuestionRequest(BaseModel):
    """RAG로 예상 문제 생성"""
    userId: str
    bookId: str
    pdf_base64: str
    max_pages: Optional[int] = None
    difficulty: DifficultyLevel
    question_type: QuestionType
    query: str


class GeneratingAdditionalQuestionRequest(BaseModel):
    """RAG로 추가 문제 생성"""
    userId: str
    bookId: str
    pdf_base64: str
    max_pages: Optional[int] = None
    difficulty: DifficultyLevel
    previous_question_type: QuestionType
    query: str


class EvaluatingAnswerRequest(BaseModel):
    """답안 평가 및 로깅"""
    userId: str
    bookId: str
    question: str
    user_answer: str
    correct_answer: str
    explanation: str


class ConceptExplanationRequest(BaseModel):
    """개념 설명"""
    userId: str
    bookId: str
    pdf_base64: str
    max_pages: Optional[int] = None
    concept_query: str
    user_level: DifficultyLevel


class ReexplainingConceptRequest(BaseModel):
    """개념 재설명"""
    userId: str
    bookId: str
    pdf_base64: str
    max_pages: Optional[int] = None
    original_concept: str
    user_feedback: str
    difficulty_level: DifficultyLevel


class PageSearchRequest(BaseModel):
    """페이지 검색 후 결과 처리"""
    userId: str
    bookId: str
    pdf_base64: str
    max_pages: Optional[int] = None
    search_keyword: str
    search_type: SearchType
    max_results: Optional[int] = 10