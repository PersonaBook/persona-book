from pydantic import BaseModel
from typing import List, Optional
from app.schemas.tool_input import UserInfoTool, ProblemInfoTool


class LowUnderstandingAttemptSummary(BaseModel):
    text: str
    feedback: str
    score: int


class PreprocessedLearningResponse(BaseModel):
    user_info: UserInfoTool
    low_understanding_attempts_summary: List[LowUnderstandingAttemptSummary]
    best_attempt_text: str
    problem_info: ProblemInfoTool


class ExternalSearchResponse(BaseModel):
    status: str
    message: str
    num_indexed: Optional[int] = None
    errors: List[str] = []


class LearningMaterialSearchResult(BaseModel):
    id: str
    content_text: str
    url: str
    title: str
    score: float
    material_type: Optional[str] = None
    difficulty_level: Optional[str] = None


class LearningSearchResponse(BaseModel):
    status: str
    message: str
    results: List[LearningMaterialSearchResult] = []
    total_hits: int
    query_vector_dimension: Optional[int] = None
