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