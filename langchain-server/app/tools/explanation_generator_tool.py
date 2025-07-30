from typing import Type, List
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.schemas.tool_input import (
    ExplanationGeneratorToolInput,
    UserInfoTool,
    ProblemInfoTool,
    LowUnderstandingAttemptSummaryTool,
)
from app.core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI


class ExplanationGeneratorTool(BaseTool):
    name: str = "ExplanationGeneratorTool"
    description: str = (
        "주어진 학습 자료와 사용자 컨텍스트를 기반으로 설명을 생성합니다."
    )
    args_schema: Type[BaseModel] = ExplanationGeneratorToolInput
    llm: ChatGoogleGenerativeAI = Field(exclude=True)

    def __init__(self, llm: ChatGoogleGenerativeAI, **kwargs):
        super().__init__(llm=llm, **kwargs)
        self.llm = llm

    async def _arun(
        self,
        learning_materials: List[dict],
        user_info: UserInfoTool,
        problem_info: ProblemInfoTool,
        low_understanding_attempts_summary: List[LowUnderstandingAttemptSummaryTool],
        best_attempt_text: str,
    ) -> str:
        materials_text = "\n\n".join(
            [mat.get("content_text", "") for mat in learning_materials]
        )

        summary_text = "\n".join(
            [
                f"- {s.text} (피드백: {s.feedback}, 점수: {s.score})"
                for s in low_understanding_attempts_summary
            ]
        )

        prompt = f"""
            당신은 학습자에게 개념을 설명하는 데 특화된 AI 튜터입니다.
            사용자의 실수를 분석하고, 오개념을 바로잡아 실제 이해로 이어질 수 있도록 설명을 생성하세요.

            ---

            [사용자 정보]
            - 나이: {user_info.age}세
            - 학습 배경: {user_info.learning_experience} 수준

            ---

            [문제 정보]
        - 도메인: {problem_info.domain}
        - 문제 개념: {problem_info.concept}
        - 문제 내용: "{problem_info.problem_text}"
        - 사용자 답변: "{problem_info.user_answer}"
        - 정답: "{problem_info.correct_answer}"

            ---

            [과거 실패한 설명 시도]
            사용자가 과거에 잘 이해하지 못했던 설명입니다.
            비슷한 용어나 표현은 피하고, **다른 관점 또는 더 쉬운 비유**를 사용해주세요.

            {summary_text}

            ---

            [사용자가 가장 잘 이해한 설명]
            "{best_attempt_text}"

            ---

            [참고 학습 자료 요약]
            설명에 참고할 수 있는 자료입니다. 그대로 복사하지 말고, 사용자의 수준에 맞게 **다시 풀어 설명**해주세요.

            {materials_text}

            ---

            [설명 요청]

            - 사용자의 나이와 배경을 고려해 **초보자에게 친절한 용어, 예시, 비유**를 사용하세요.
            - 사용자의 오답에서 드러난 오개념을 **정확히 짚고**, 올바른 개념을 명확히 설명하세요.
            - 사용자가 **자료형, 배열, 문법 등을 혼동**하고 있는지 확인하고, 이를 **비유나 상황 예시로 쉽게 풀어주세요.**
            - 실패한 설명의 어투, 형식은 피하고, 성공한 설명처럼 **간결하고 일상적인 표현**을 중심으로 구성하세요.
            - 설명은 **짧은 단락 1~2개**로 구성하고, 최대한 **시각적 상상(비유, 물건 등)**을 유도해주세요.
            - 목표는 단순히 정답을 알려주는 것이 아니라, **오개념을 교정하고 "아하!" 하고 이해할 수 있도록 돕는 것**입니다.
         """

        response = await self.llm.ainvoke(prompt)
        return response.content

    def _run(
        self,
        learning_materials: List[dict],
        user_info: UserInfoTool,
        problem_info: ProblemInfoTool,
        low_understanding_attempts_summary: List[LowUnderstandingAttemptSummaryTool],
        best_attempt_text: str,
    ) -> str:
        raise NotImplementedError(
            "ExplanationGeneratorTool does not support synchronous execution."
        )


async def get_explanation_generator_tool() -> ExplanationGeneratorTool:
    llm_instance = ChatGoogleGenerativeAI(
        model=settings.gemini_model_name, google_api_key=settings.gemini_api_key
    )
    return ExplanationGeneratorTool(llm=llm_instance)
