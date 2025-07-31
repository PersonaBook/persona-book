from pydantic import BaseModel, Field
from typing import List, Optional


class UserInfoTool(BaseModel):
    user_id: int
    age: int
    learning_experience: str


class LowUnderstandingAttemptSummaryTool(BaseModel):
    text: str
    feedback: str
    score: int


class ProblemInfoTool(BaseModel):
    concept: str
    problem_text: str
    user_answer: str
    correct_answer: str
    domain: str


class LearningMaterialSearchToolInput(BaseModel):
    user_info: UserInfoTool
    low_understanding_attempts_summary: List[LowUnderstandingAttemptSummaryTool]
    best_attempt_text: Optional[str] = None
    problem_info: ProblemInfoTool


class GoogleSearchToolInput(BaseModel):
    concept: str = Field(...)
    domain: str = Field(...)


class ExplanationGeneratorToolInput(BaseModel):
    learning_materials: List[dict] = Field(
        ...,
        description="List of learning materials (dictionaries) to generate explanation from.",
    )
    user_info: UserInfoTool = Field(..., description="User's information.")
    problem_info: ProblemInfoTool = Field(..., description="Problem information.")
    low_understanding_attempts_summary: List[LowUnderstandingAttemptSummaryTool] = Field(
        ..., description="Summary of previous low understanding attempts."
    )
    best_attempt_text: Optional[str] = Field(
        None, description="Text of the best previous explanation."
    )
