from typing import Type, List
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.schemas.tool_input import (
    LearningMaterialSearchToolInput,
    UserInfoTool,
    LowUnderstandingAttemptSummaryTool,
    ProblemInfoTool,
)
from app.schemas.response.learning import LearningMaterialSearchResult
from app.services.learning_service import LearningService
from app.repository.learning_material_repository import LearningMaterialRepository
from app.core.elasticsearch_client import ElasticsearchClient
from app.services.embedding_service import EmbeddingService


class LearningMaterialSearchTool(BaseTool):
    name: str = "LearningMaterialSearchTool"
    description: str = (
        "사용자의 질문과 학습 수준에 맞는 학습 자료를 Elasticsearch에서 검색합니다."
    )
    args_schema: Type[BaseModel] = LearningMaterialSearchToolInput
    learning_service: LearningService = Field(exclude=True)

    async def _arun(
        self,
        user_info: UserInfoTool,
        low_understanding_attempts_summary: List[LowUnderstandingAttemptSummaryTool],
        best_attempt_text: str,
        problem_info: ProblemInfoTool,
    ) -> List[LearningMaterialSearchResult]:
        """비동기적으로 학습 자료를 검색합니다."""
        query = f"{problem_info.domain} {problem_info.concept}"
        learning_experience = user_info.learning_experience

        results = await self.learning_service.search_learning_materials_for_tool(
            concept=query,  # Pass the combined query to the service
            learning_experience=learning_experience,
            problem_text=problem_info.problem_text,  # Keep problem_text for potential future use in the service
        )
        return results

    def _run(
        self,
        user_info: UserInfoTool,
        low_understanding_attempts_summary: List[LowUnderstandingAttemptSummaryTool],
        best_attempt_text: str,
        problem_info: ProblemInfoTool,
    ) -> List[LearningMaterialSearchResult]:
        """동기적으로 학습 자료를 검색합니다. (비동기 _arun을 사용하므로 이 메서드는 사용되지 않을 수 있습니다.)"""
        raise NotImplementedError(
            "LearningMaterialSearchTool does not support synchronous execution."
        )


async def get_learning_material_search_tool() -> LearningMaterialSearchTool:
    es_client = await ElasticsearchClient.get_client()
    embedding_service = EmbeddingService()
    await embedding_service.ainitialize()
    repo = LearningMaterialRepository(es_client, embedding_service)
    service = LearningService(repo)
    return LearningMaterialSearchTool(learning_service=service)
