from pydantic import BaseModel
from enum import Enum
from typing import Optional

class FeatureContext(str, Enum):
    INITIAL = "INITIAL"
    PROBLEM_GENERATION = "PROBLEM_GENERATION"
    PROBLEM_SOLVING = "PROBLEM_SOLVING"
    CONCEPT_EXPLANATION = "CONCEPT_EXPLANATION"

class StageContext(str, Enum):
    START = "START"
    SELECT_TYPE = "SELECT_TYPE"
    SELECT_PROBLEM_TYPE = "SELECT_PROBLEM_TYPE"
    PROMPT_CHAPTER_PAGE = "PROMPT_CHAPTER_PAGE"
    PROMPT_CONCEPT = "PROMPT_CONCEPT"
    GENERATING_PROBLEM = "GENERATING_PROBLEM"
    PROBLEM_PRESENTED = "PROBLEM_PRESENTED"
    USER_ANSWER = "USER_ANSWER"
    CORRECT_FEEDBACK = "CORRECT_FEEDBACK"
    INCORRECT_FEEDBACK = "INCORRECT_FEEDBACK"
    EXPLANATION_PRESENTED = "EXPLANATION_PRESENTED"
    FEEDBACK_RATING = "FEEDBACK_RATING"
    PROMPT_FEEDBACK_TEXT = "PROMPT_FEEDBACK_TEXT"
    INPUT_FEEDBACK_TEXT = "INPUT_FEEDBACK_TEXT"
    RE_EXPLANATION_PRESENTED = "RE_EXPLANATION_PRESENTED"
    PROMPT_NEXT_ACTION = "PROMPT_NEXT_ACTION"

class UserMessageDto(BaseModel):
    userId: str
    bookId: int
    content: str
    sender: str
    messageType: str
    featureContext: Optional[FeatureContext] = FeatureContext.INITIAL
    stageContext: Optional[StageContext] = StageContext.START

class AiMessageDto(BaseModel):
    userId: str
    bookId: int
    sender: str = "AI"
    content: str
    messageType: str = "TEXT"
    featureContext: FeatureContext
    stageContext: StageContext