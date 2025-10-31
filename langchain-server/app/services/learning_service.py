from typing import List
from app.schemas.request.learning import (
    ExplanationRequest,
    ExternalSearchRequest,
    LearningSearchRequest,
)
from app.schemas.response.learning import (
    LearningSearchResponse,
    LearningMaterialSearchResult,
    PreprocessedLearningResponse,
    LowUnderstandingAttemptSummary,
)
from app.schemas.tool_input import UserInfoTool, ProblemInfoTool
from app.services.external_search_service import ExternalSearchService
from app.services.crawler import extract_text_from_url
from app.utils.crawler.text_processing import chunk_text
from app.services.embedding_service import EmbeddingService
from app.repository.learning_material_repository import LearningMaterialRepository
from app.entity.learning_material import LearningMaterial
from app.services.gemini_summary_service import GeminiSummaryService
import uuid
import asyncio


class LearningService:
    def __init__(self, learning_material_repo: LearningMaterialRepository):
        self.external_search_service = ExternalSearchService()
        self.embedding_service = EmbeddingService()
        self.learning_material_repo = learning_material_repo
        self.gemini_summary_service = GeminiSummaryService()

    async def preprocess_learning_request(
            self, request: ExplanationRequest
    ) -> PreprocessedLearningResponse:
        summaries = await asyncio.gather(
            *[
                self.gemini_summary_service.summarize_text(
                    attempt.explanation_text,
                    attempt.feedback_text,
                    attempt.understanding_score,
                )
                for attempt in request.low_understanding_attempts
            ]
        ) if request.low_understanding_attempts else []

        result = PreprocessedLearningResponse(
            user_info=UserInfoTool(**request.user_info.dict()),
            low_understanding_attempts_summary=[
                LowUnderstandingAttemptSummary(**s) for s in summaries
            ],
            best_attempt_text=(
                request.best_attempt.explanation_text if request.best_attempt and request.best_attempt.explanation_text else None
            ),
            problem_info=ProblemInfoTool(**request.problem_info.dict()),
        )
        print("[LearningService] Preprocessed learning request result:")
        print(result)
        return result

    async def process_external_search_and_index(
            self, request: ExternalSearchRequest
    ) -> List[LearningMaterialSearchResult]:
        print(
            f"Processing external search and indexing for query: '{request.query}' with site_restrict: {request.site_restrict if hasattr(request, 'site_restrict') else 'None'}"
        )

        search_results = await self.external_search_service.search_learning_materials(
            query=request.query,
            num_results=10,
            site_restrict=(
                request.site_restrict if hasattr(request, "site_restrict") else None
            ),
        )

        indexed_materials = []
        errors = []

        for item in search_results:
            url = item.get("link")
            title = item.get("title", "No Title")

            if not url:
                errors.append(f"Skipping item due to missing URL: {item.get('title')}")
                continue

            if await self.learning_material_repo.is_url_indexed(url):
                print(f"URL already indexed, skipping: {url}")
                continue

            print(f"Attempting to extract content from: {url}")
            content = extract_text_from_url(url)

            if content:
                print(f"Content extracted from {url}. Length: {len(content)} chars.")

                content_chunks_data = chunk_text(content, url, title)

                for chunk_data in content_chunks_data:
                    chunk_content = chunk_data["content"]

                    print(f"Generating embedding for chunk from {url}...")
                    embedding = await self.embedding_service.get_embedding(
                        chunk_content
                    )

                    material_id = str(uuid.uuid4())
                    material = LearningMaterial(
                        id=material_id,
                        concept=request.concept,
                        content_text=chunk_content,
                        content_embedding=embedding,
                        url=url,
                        title=title,
                        material_type="EXTERNAL",
                        difficulty_level=self._map_difficulty_level(url),
                        source=self._map_source(url),
                        tags=[],
                    )
                    indexed_materials.append(material)

            else:
                print(f"Failed to extract content from: {url}")
                errors.append(f"Content extraction failed for {url}")

        if indexed_materials:
            try:
                await self.learning_material_repo.bulk_save_materials(indexed_materials)
                print(
                    f"Successfully indexed {len(indexed_materials)} chunks into Elasticsearch."
                )
            except Exception as e:
                errors.append(f"Error during bulk indexing: {e}")
                print(f"Bulk indexing failed: {e}")

        formatted_results = [
            LearningMaterialSearchResult(
                id=mat.id,
                content_text=mat.content_text,
                url=mat.url,
                title=mat.title,
                score=0.0,
                material_type=mat.material_type,
                difficulty_level=mat.difficulty_level,
                source=mat.source,
            )
            for mat in indexed_materials
        ]
        return formatted_results

    def _map_difficulty_level(self, url: str) -> str:
        if "w3schools.com" in url:
            return "BEGINNER"
        elif "geeksforgeeks.org" in url:
            return "INTERMEDIATE"
        elif "oracle.com" in url:
            return "ADVANCED"
        return "UNKNOWN"

    def _map_source(self, url: str) -> str:
        if "w3schools.com" in url:
            return "W3Schools"
        elif "geeksforgeeks.org" in url:
            return "GeeksForGeeks"
        elif "oracle.com" in url:
            return "Oracle Docs"
        return "UNKNOWN"

    async def search_learning_materials(
            self, request: LearningSearchRequest
    ) -> LearningSearchResponse:
        print(
            f"Searching learning materials for query: '{request.query}' with search_type: '{request.search_type}'"
        )

        query_embedding = None
        if request.search_type in ["vector", "hybrid"]:
            print(f"Generating embedding for query: '{request.query}'")
            query_embedding = await self.embedding_service.get_embedding(request.query)
            if not query_embedding:
                return LearningSearchResponse(
                    status="failed",
                    message="Failed to generate embedding for query.",
                    results=[],
                    total_hits=0,
                )

        filters = {}
        if request.concept:
            filters["concept.keyword"] = request.concept
        if request.user_experience_level:
            filters["difficulty_level.keyword"] = request.user_experience_level

        search_results: List[LearningMaterial] = []
        total_hits = 0

        if request.search_type == "vector" and query_embedding:
            search_results = (
                await self.learning_material_repo.search_by_vector_similarity(
                    embedding=query_embedding, size=request.top_k, filters=filters
                )
            )
            total_hits = len(
                search_results
            )  # 실제 total_hits는 더 많을 수 있지만 여기서는 반환된 개수만 카운트

        elif request.search_type == "keyword":
            search_results, total_hits = (
                await self.learning_material_repo.search_by_keyword(
                    query=request.query, size=request.top_k, filters=filters
                )
            )

        elif request.search_type == "hybrid" and query_embedding:
            search_results, total_hits = (
                await self.learning_material_repo.hybrid_search(
                    query_text=request.query,
                    query_embedding=query_embedding,
                    size=request.top_k,
                    filters=filters,
                )
            )
        else:
            return LearningSearchResponse(
                status="failed",
                message="Invalid search type or missing query embedding for vector/hybrid search.",
                results=[],
                total_hits=0,
            )

        formatted_results = [
            LearningMaterialSearchResult(
                id=mat.id,
                content_text=mat.content_text,
                url=mat.url,
                title=mat.title,
                score=mat.score if hasattr(mat, "score") else 0.0,
                material_type=mat.material_type,
                difficulty_level=mat.difficulty_level,
            )
            for mat in search_results
        ]

        return LearningSearchResponse(
            status="success",
            message=f"Successfully retrieved {len(formatted_results)} learning materials.",
            results=formatted_results,
            total_hits=total_hits,
            query_vector_dimension=len(query_embedding) if query_embedding else None,
        )

    async def search_learning_materials_for_tool(
            self, concept: str, learning_experience: str, problem_text: str, top_k: int = 5
    ) -> List[LearningMaterialSearchResult]:
        # 난이도 우선순위 매핑
        difficulty_priority = {
            "BEGINNER": ["BEGINNER", "INTERMEDIATE", "ADVANCED"],
            "HAS_PROJECT_EXPERIENCE": ["INTERMEDIATE", "ADVANCED", "BEGINNER"],
            "MAJOR_STUDENT": ["INTERMEDIATE", "ADVANCED", "BEGINNER"],
            "PROFESSIONAL_DEVELOPER": ["ADVANCED", "INTERMEDIATE", "BEGINNER"],
        }

        # 문제 내용 임베딩
        problem_embedding = await self.embedding_service.get_embedding(problem_text)
        if not problem_embedding:
            return []

        results = []
        # 난이도별 검색 및 fallback
        for difficulty in difficulty_priority.get(learning_experience, []):
            filters = {
                "concept.keyword": concept,
                "difficulty_level.keyword": difficulty,
            }
            search_results = (
                await self.learning_material_repo.search_by_vector_similarity(
                    embedding=problem_embedding,
                    size=top_k,
                    filters=filters,
                )
            )
            if search_results:
                results.extend(search_results)
                break

        formatted_results = [
            LearningMaterialSearchResult(
                id=mat.id,
                content_text=mat.content_text,
                url=mat.url,
                title=mat.title,
                score=mat.score if hasattr(mat, "score") else 0.0,
                material_type=mat.material_type,
                difficulty_level=mat.difficulty_level,
                source=mat.source,
            )
            for mat in results
        ]
        return formatted_results

    async def generate_concept_explanation(
        self, concept: str, user_experience_level: str = None
    ) -> str:
        """
        RAG 기반 개념 설명 생성 (초기 설명용)

        Args:
            concept: 설명할 개념 (예: "데드락", "DFS")
            user_experience_level: 사용자 경험 수준

        Returns:
            생성된 개념 설명
        """
        print(f"[LearningService] 개념 설명 생성 시작: {concept}")

        # 1. PDF 벡터 스토어에서 직접 검색
        from langchain_community.vectorstores import ElasticsearchStore
        from langchain_openai import OpenAIEmbeddings
        from app.core.config import settings

        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key
        )

        vector_store = ElasticsearchStore(
            embedding=embeddings,
            es_url="http://elasticsearch:9200",
            index_name="java_learning_docs"  # PDF 인덱스
        )

        print(f"[LearningService] PDF 벡터 스토어에서 '{concept}' 검색 중...")
        relevant_docs = vector_store.similarity_search(concept, k=5)
        print(f"[LearningService] 검색 결과: {len(relevant_docs)}개")

        # 2. 검색된 자료를 컨텍스트로 사용
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(doc.page_content)

        context = "\n\n---\n\n".join(context_parts) if context_parts else "관련 자료가 없습니다."
        print(f"[LearningService] 컨텍스트 길이: {len(context)}자")

        # 3. Gemini로 설명 생성
        from langchain_google_genai import ChatGoogleGenerativeAI
        from app.core.config import settings

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.3,
            google_api_key=settings.gemini_api_key
        )

        prompt = f"""다음 개념에 대해 명확하고 이해하기 쉽게 설명해주세요.

개념: {concept}
사용자 수준: {user_experience_level or "일반"}

참고 자료:
{context}

요구사항:
1. 개념의 정의를 명확히 설명
2. 실생활 또는 프로그래밍 예시 포함
3. 핵심 포인트 강조
4. {user_experience_level or "일반"} 수준에 맞는 용어 사용
5. 간결하고 이해하기 쉬운 설명 (500자 이내)

설명:"""

        print(f"[LearningService] LLM 호출 중...")
        response = llm.invoke(prompt)
        print(f"[LearningService] 설명 생성 완료: {len(response.content)}자")

        return response.content