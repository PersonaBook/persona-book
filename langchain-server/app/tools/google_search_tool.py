from typing import Type, List
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from app.schemas.tool_input import GoogleSearchToolInput
from app.schemas.request.learning import ExternalSearchRequest
from app.schemas.response.learning import LearningMaterialSearchResult
from app.services.learning_service import LearningService
from app.repository.learning_material_repository import LearningMaterialRepository
from app.core.elasticsearch_client import ElasticsearchClient
from app.services.embedding_service import EmbeddingService


class GoogleSearchTool(BaseTool):
    name: str = "GoogleSearchTool"
    description: str = (
        "LearningMaterialSearchTool로 충분한 자료가 검색되지 않았을 때, "
        "Google Custom Search API를 활용해 외부 웹사이트에서 학습 자료를 수집하고 "
        "그 자료를 벡터화하여 저장하는 역할을 수행합니다."
    )
    args_schema: Type[BaseModel] = GoogleSearchToolInput
    learning_service: LearningService = Field(exclude=True)

    async def _arun(
        self, concept: str, domain: str
    ) -> List[LearningMaterialSearchResult]:
        """비동기적으로 Google 검색을 수행하고 학습 자료를 저장합니다."""
        query = f"{domain} {concept}"
        # 제한된 도메인 내에서 검색
        domains = ["w3schools.com", "geeksforgeeks.org", "oracle.com"]
        site_restrict = " OR ".join([f"site:{d}" for d in domains])

        # LearningService의 process_external_search_and_index 메서드 재사용
        # 이 메서드는 검색, 크롤링, 정제, 난이도 태깅, 임베딩, 저장을 모두 처리합니다.
        results = await self.learning_service.process_external_search_and_index(
            request=ExternalSearchRequest(
                query=query,
                concept=concept,
                user_experience_level=None,  # GoogleSearchTool에서는 user_experience_level을 알 수 없으므로 None
                site_restrict=site_restrict,
            )
        )
        return results

    def _run(
        self, concept: str, problem_text: str
    ) -> List[LearningMaterialSearchResult]:
        """동기적으로 Google 검색을 수행합니다. (비동기 _arun을 사용하므로 이 메서드는 사용되지 않을 수 있습니다.)"""
        raise NotImplementedError(
            "GoogleSearchTool does not support synchronous execution."
        )


# Dependency for the tool
async def get_google_search_tool() -> GoogleSearchTool:
    es_client = await ElasticsearchClient.get_client()
    embedding_service = EmbeddingService()
    await embedding_service.ainitialize()
    repo = LearningMaterialRepository(es_client, embedding_service)
    service = LearningService(repo)
    return GoogleSearchTool(learning_service=service)
