from langchain_google_genai import ChatGoogleGenerativeAI
import json
from app.core.config import settings


class GeminiSummaryService:
    def __init__(self):
        self.model = ChatGoogleGenerativeAI(
            model=settings.gemini_model_name, google_api_key=settings.gemini_api_key
        )

    async def summarize_text(self, explanation: str, feedback: str, score: int) -> dict:
        prompt = f"""
        당신은 학습 데이터를 요약해주는 조수입니다.

        아래는 사용자가 특정 개념에 대해 충분히 이해하지 못했던 설명 시도들입니다.
        각 시도에는 다음 정보가 포함되어 있습니다:

        - 사용자가 받은 **설명 내용**
        - 설명에 대한 **사용자 피드백** (이해하지 못한 이유나 개선 요청)
        - 사용자 스스로 평가한 **이해도 점수** (정수, 예: 1~5)

        이 데이터들은 나중에 LLM이 새로운 설명을 만들 때
        “과거 어떤 설명이 실패했는지”를 참고하기 위한 것입니다.

        따라서, 각 시도별로 **짧고 핵심적인 요약**을 만들어 주세요.
        불필요한 말은 제거하고, 문제의 핵심과 피드백 내용을 중심으로 정리해주세요.

        ---

        출력 형식은 다음 JSON 형태로 해주세요:

        ```json
        {{
          "text": "설명 내용의 요약된 표현",
          "feedback": "사용자의 피드백 요약",
          "score": {score}
        }}
        ```

        다음은 요약 대상 데이터입니다:

        설명: "{explanation}"
        피드백: "{feedback}"
        이해도 점수: {score}
        """
        response = await self.model.ainvoke(prompt)
        json_string = (
            response.content.strip().replace("```json", "").replace("```", "").strip()
        )
        summary = json.loads(json_string)
        return summary
