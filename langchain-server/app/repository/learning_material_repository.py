from typing import List, Dict, Any, Optional, Tuple
from elasticsearch import AsyncElasticsearch
from app.core.config import settings
from app.entity.learning_material import LearningMaterial
from app.services.embedding_service import EmbeddingService
from elasticsearch.helpers import async_bulk
from datetime import datetime


class LearningMaterialRepository:
    def __init__(
        self, es_client: AsyncElasticsearch, embedding_service: EmbeddingService
    ):
        self.es_client = es_client
        self.embedding_service = embedding_service
        self.index_name = settings.elasticsearch_index_learning_materials
        self.vector_dim = self.embedding_service.embedding_dimension

    async def create_index(self):
        es = self.es_client
        if not await es.indices.exists(index=self.index_name):
            print(
                f"Creating index: {self.index_name} with vector dimension: {self.vector_dim}"
            )
            await es.indices.create(
                index=self.index_name,
                body={
                    "mappings": {
                        "properties": {
                            "content_text": {"type": "text"},
                            "concept": {"type": "keyword"},
                            "difficulty_level": {"type": "keyword"},
                            "url": {"type": "keyword"},
                            "title": {"type": "text"},
                            "material_type": {"type": "keyword"},
                            "content_embedding": {
                                "type": "dense_vector",
                                "dims": self.vector_dim,
                                "index": "true",
                                "similarity": "l2_norm",
                            },
                            "feedback_embedding": {
                                "type": "dense_vector",
                                "dims": self.vector_dim,
                            },
                            "created_at": {"type": "date"},
                            "updated_at": {"type": "date"},
                            "success_count": {"type": "integer"},
                            "total_attempts_count": {"type": "integer"},
                            "average_understanding_score": {"type": "float"},
                        }
                    }
                },
            )
            print(f"Index {self.index_name} created.")
        else:
            print(f"Index {self.index_name} already exists.")

    async def save_material(self, material: LearningMaterial) -> str:
        await self.create_index()
        es = self.es_client
        doc = material.to_elasticsearch_doc()
        if material.id:
            response = await es.index(
                index=self.index_name, id=material.id, document=doc
            )
        else:
            response = await es.index(index=self.index_name, document=doc)
        material_id = response["_id"]
        print(f"Saved learning material with ID: {material_id}")
        return material_id

    async def bulk_save_materials(self, materials: List[LearningMaterial]):
        es = self.es_client
        actions = []
        for material in materials:
            doc = material.to_elasticsearch_doc()
            action = {"_index": self.index_name, "_source": doc}
            if material.id:
                action["_id"] = material.id
            actions.append(action)
        await async_bulk(es, actions)
        print(f"Bulk saved {len(materials)} learning materials.")

    async def get_material_by_id(self, material_id: str) -> Optional[LearningMaterial]:
        es = self.es_client
        try:
            response = await es.get(index=self.index_name, id=material_id)
            if response["found"]:
                return LearningMaterial.from_elasticsearch_doc(
                    response["_id"], response["_source"]
                )
            return None
        except Exception as e:
            print(f"Error getting material by ID {material_id}: {e}")
            return None

    async def search_materials_by_concept(
        self, concept: str, size: int = 5
    ) -> List[LearningMaterial]:
        es = self.es_client
        query = {"query": {"match": {"concept": concept}}, "size": size}
        response = await es.search(index=self.index_name, body=query)
        return [
            LearningMaterial.from_elasticsearch_doc(hit["_id"], hit["_source"])
            for hit in response["hits"]["hits"]
        ]

    async def search_by_vector_similarity(
        self, embedding: List[float], size: int = 5, filters: Optional[Dict] = None
    ) -> List[LearningMaterial]:
        es = self.es_client
        knn_query = {
            "field": "content_embedding",
            "query_vector": embedding,
            "k": size,
            "num_candidates": max(100, size * 10),
        }
        body: Dict[str, Any] = {
            "knn": knn_query,
            "_source": [
                "content_text",
                "url",
                "title",
                "material_type",
                "difficulty_level",
                "concept",
            ],
        }
        if filters:
            body["query"] = {"bool": {"filter": []}}
            for key, value in filters.items():
                body["query"]["bool"]["filter"].append({"term": {key: value}})
        response = await es.search(index=self.index_name, body=body, size=size)
        results = []
        for hit in response["hits"]["hits"]:
            material = LearningMaterial.from_elasticsearch_doc(
                hit["_id"], hit["_source"]
            )
            material.score = hit.get("_score", 0.0)
            results.append(material)
        return results

    async def search_by_keyword(
        self, query: str, size: int = 5, filters: Optional[Dict] = None
    ) -> Tuple[List[LearningMaterial], int]:
        es = self.es_client
        query_body = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query,
                                "fields": ["content_text", "title", "concept"],
                            }
                        }
                    ]
                }
            },
            "size": size,
            "_source": [
                "content_text",
                "url",
                "title",
                "material_type",
                "difficulty_level",
                "concept",
            ],
        }
        if filters:
            query_body["query"]["bool"]["filter"] = []
            for key, value in filters.items():
                query_body["query"]["bool"]["filter"].append({"term": {key: value}})
        response = await es.search(index=self.index_name, body=query_body)
        results = []
        for hit in response["hits"]["hits"]:
            material = LearningMaterial.from_elasticsearch_doc(
                hit["_id"], hit["_source"]
            )
            material.score = hit.get("_score", 0.0)
            results.append(material)
        return results, response["hits"]["total"]["value"]

    async def hybrid_search(
        self,
        query_text: str,
        query_embedding: List[float],
        size: int = 5,
        filters: Optional[Dict] = None,
    ) -> Tuple[List[LearningMaterial], int]:
        es = self.es_client
        knn_query = {
            "field": "content_embedding",
            "query_vector": query_embedding,
            "k": size,
            "num_candidates": max(100, size * 10),
            "boost": 0.8,
        }
        match_query = {
            "multi_match": {
                "query": query_text,
                "fields": ["content_text", "title", "concept"],
                "fuzziness": "AUTO",
                "boost": 0.2,
            }
        }
        filter_clauses = []
        if filters:
            for key, value in filters.items():
                filter_clauses.append({"term": {key: value}})
        query_body: Dict[str, Any] = {
            "query": {"bool": {"must": [match_query]}},
            "knn": knn_query,
            "size": size,
            "_source": [
                "content_text",
                "url",
                "title",
                "material_type",
                "difficulty_level",
                "concept",
            ],
        }
        if filter_clauses:
            query_body["query"]["bool"]["filter"] = filter_clauses
        response = await es.search(index=self.index_name, body=query_body)
        results = []
        for hit in response["hits"]["hits"]:
            material = LearningMaterial.from_elasticsearch_doc(
                hit["_id"], hit["_source"]
            )
            material.score = hit.get("_score", 0.0)
            results.append(material)
        total_hits = response["hits"]["total"]["value"]
        return results, total_hits

    async def update_success_count(self, material_id: str, increment: int = 1):
        es = self.es_client
        try:
            await es.update(
                index=self.index_name,
                id=material_id,
                script={
                    "source": "ctx._source.success_count += params.count; ctx._source.updated_at = params.now",
                    "lang": "painless",
                    "params": {
                        "count": increment,
                        "now": datetime.utcnow().isoformat() + "Z",
                    },
                },
            )
            print(f"Updated success_count for material ID: {material_id}")
        except Exception as e:
            print(f"Error updating success_count for {material_id}: {e}")

    async def is_url_indexed(self, url: str) -> bool:
        es = self.es_client
        query = {"query": {"term": {"url.keyword": url}}}
        response = await es.search(index=self.index_name, body=query, size=0)
        return response["hits"]["total"]["value"] > 0

    async def search_and_sort_by_effectiveness(
        self,
        concept: str,
        user_level: str,
        exclude_ids: Optional[List[str]] = None,
        size: int = 1,
    ) -> Optional[LearningMaterial]:
        es = self.es_client
        query_body = {
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"concept.keyword": concept}},
                        {"term": {"difficulty_level.keyword": user_level}},
                    ]
                }
            },
            "sort": [
                {"success_count": {"order": "desc"}},
                {"average_understanding_score": {"order": "desc", "missing": "_last"}},
            ],
            "size": size,
        }
        if exclude_ids:
            query_body["query"]["bool"]["must_not"] = [{"ids": {"values": exclude_ids}}]
        response = await es.search(index=self.index_name, body=query_body)
        if response["hits"]["hits"]:
            material = LearningMaterial.from_elasticsearch_doc(
                response["hits"]["hits"][0]["_id"],
                response["hits"]["hits"][0]["_source"],
            )
            material.score = response["hits"]["hits"][0].get("_score", 0.0)
            return material
        return None
