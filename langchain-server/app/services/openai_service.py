from openai import OpenAI
from app.schemas.openai_chat import OpenAIChatRequest
from app.core.config import settings

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def ask_openai(self, req: OpenAIChatRequest) -> str:
        prompt = f"""
        사용자의 정보:
        - 나이: {req.age}
        - 배경: {req.background}
        이전 답변에 대한 피드백: {req.feedback}
        
        아래 질문에 대해 위의 정보를 참고하여, 사용자의 수준에 맞는 답변을 해주세요.
        질문: {req.question}
        """
        response = self.client.chat.completions.create(
            model=settings.openai_model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

openai_service = OpenAIService()
