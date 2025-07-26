from app.core.config import settings
from app.entity.chat_history import ChatHistory
from app.repository.chat_history_repository import chat_history_repository
from app.schemas.request.openai_chat import OpenAIChatRequest
from openai import OpenAI


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def ask_openai(self, req: OpenAIChatRequest) -> str:
        # prompt = f"""
        # 사용자의 정보:
        # - 나이: {req.age}
        # - 배경: {req.background}
        # 이전 답변에 대한 피드백: {req.feedback}

        # 아래 질문에 대해 위의 정보를 참고하여, 사용자의 수준에 맞는 답변을 해주세요.
        # 질문: {req.question}
        # """

        # OpenAI API 호출 (주석 처리)
        # response = self.client.chat.completions.create(
        #     model=settings.openai_model_name,
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # answer = response.choices[0].message.content

        # Mock 응답 (개발/테스트용)
        answer = self._get_mock_response(req)

        # 응답을 Elasticsearch에 저장
        try:
            chat_history = ChatHistory(
                age=req.age,
                background=req.background,
                feedback=req.feedback,
                question=req.question,
                answer=answer,
                model_name=settings.openai_model_name,
            )

            history_id = chat_history_repository.save_chat_history(chat_history)
            print(f"Chat history saved with ID: {history_id}")
        except Exception as e:
            print(f"Failed to save chat history to Elasticsearch: {e}")

        return answer

    def _get_mock_response(self, req: OpenAIChatRequest) -> str:
        """Mock 응답 생성 (개발/테스트용)"""
        mock_responses = {
            "머신러닝": f"머신러닝은 인공지능의 한 분야로, 컴퓨터가 데이터로부터 패턴을 학습하여 예측이나 분류를 수행하는 기술입니다. {req.age}세 {req.background}이신 분께는 머신러닝의 기본 개념부터 차근차근 설명드리겠습니다.",
            "딥러닝": f"딥러닝은 머신러닝의 하위 분야로, 인공신경망을 깊게 쌓아서 복잡한 패턴을 학습하는 기술입니다. {req.background} 배경을 가진 분이시니 실무 적용 사례도 함께 설명드릴게요.",
            "인공지능": f"인공지능(AI)은 인간의 지능을 모방하여 문제를 해결하는 기술입니다. {req.age}세이신 분의 수준에 맞춰 AI의 현재와 미래에 대해 설명드리겠습니다.",
            "데이터베이스": f"데이터베이스는 체계적으로 관리되는 데이터의 집합입니다. {req.background}이신 분께는 실제 프로젝트에서 사용되는 데이터베이스 설계 방법을 중심으로 설명드리겠습니다.",
            "네트워크": f"네트워크는 여러 컴퓨터가 연결되어 데이터를 주고받는 시스템입니다. {req.age}세 {req.background}이신 분께는 네트워크의 기본 원리부터 실무 적용까지 설명드리겠습니다.",
        }

        # 질문에서 키워드 찾기
        question_lower = req.question.lower()
        for keyword, response in mock_responses.items():
            if keyword.lower() in question_lower:
                return response

        # 기본 응답
        return f"안녕하세요! {req.age}세 {req.background}이신 분의 질문에 답변드리겠습니다. '{req.question}'에 대한 답변은 다음과 같습니다. 이는 {req.background} 배경을 가진 분께 적합한 수준으로 설명드린 것입니다. 추가 질문이 있으시면 언제든 말씀해 주세요!"


openai_service = OpenAIService()
