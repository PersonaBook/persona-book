from pydantic import BaseModel

class OpenAIChatResponse(BaseModel):
    answer: str 