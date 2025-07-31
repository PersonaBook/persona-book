from app.core.elasticsearch_client import ElasticsearchClient
from app.repository.learning_material_repository import LearningMaterialRepository
from app.services.embedding_service import EmbeddingService
from elasticsearch import AsyncElasticsearch
from fastapi import Depends


async def get_es_client() -> AsyncElasticsearch:
    return await ElasticsearchClient.get_client()


async def get_learning_material_repository(
    es_client: AsyncElasticsearch = Depends(get_es_client),
) -> LearningMaterialRepository:
    embedding_service = EmbeddingService()
    await embedding_service.ainitialize()
    return LearningMaterialRepository(es_client, embedding_service)
