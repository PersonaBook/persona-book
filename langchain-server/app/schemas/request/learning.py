from pydantic import BaseModel, Field
from typing import Optional, List


class UserInfo(BaseModel):
    user_id: int
    age: Optional[int] = None
    learning_experience: Optional[str] = None


class LowUnderstandingAttempt(BaseModel):
    explanation_text: Optional[str] = None
    feedback_text: Optional[str] = None
    understanding_score: Optional[int] = None


class BestAttempt(BaseModel):
    explanation_text: Optional[str] = None
    understanding_score: Optional[int] = None


class ProblemInfo(BaseModel):
    concept: str
    problem_text: str
    user_answer: Optional[str] = None
    correct_answer: str
    domain: str


class ExplanationRequest(BaseModel):
    user_info: UserInfo
    low_understanding_attempts: List[LowUnderstandingAttempt] = []
    best_attempt: Optional[BestAttempt] = None
    problem_info: ProblemInfo


class ExternalSearchRequest(BaseModel):
    query: str = Field(...)
    concept: str = Field(...)
    user_experience_level: Optional[str] = Field(None)
    site_restrict: Optional[str] = Field(None)


class LearningSearchRequest(BaseModel):
    query: str = Field(...)
    concept: Optional[str] = Field(None)
    user_experience_level: Optional[str] = Field(None)
    search_type: str = Field("hybrid")
    top_k: int = Field(5)


class ConceptExplanationRequest(BaseModel):
    """개념 설명 요청 (초기 설명용 - 간단한 구조)"""
    user_id: int = Field(alias="userId")
    book_id: int = Field(alias="bookId")
    content: str  # 사용자가 입력한 개념 (예: "데드락", "DFS")
    user_experience_level: Optional[str] = Field(None, alias="userExperienceLevel")

    class Config:
        populate_by_name = True  # alias와 원래 이름 모두 허용