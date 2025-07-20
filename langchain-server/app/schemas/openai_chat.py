from pydantic import BaseModel

class OpenAIChatRequest(BaseModel):
    age: int
    background: str  # '전공자', '비전공자', '실무자' 중 하나
    feedback: str
    question: str

class OpenAIChatResponse(BaseModel):
    answer: str 