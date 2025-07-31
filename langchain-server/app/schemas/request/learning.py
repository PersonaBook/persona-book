from pydantic import BaseModel, Field
from typing import Optional, List


class UserInfo(BaseModel):
    user_id: int
    age: int
    learning_experience: str


class LowUnderstandingAttempt(BaseModel):
    explanation_text: str
    feedback_text: str
    understanding_score: int


class BestAttempt(BaseModel):
    explanation_text: str
    understanding_score: int


class ProblemInfo(BaseModel):
    concept: str
    problem_text: str
    user_answer: str
    correct_answer: str
    domain: str


class ExplanationRequest(BaseModel):
    user_info: UserInfo
    low_understanding_attempts: List[LowUnderstandingAttempt]
    best_attempt: BestAttempt
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
