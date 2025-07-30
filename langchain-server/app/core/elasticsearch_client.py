from app.core.config import settings
from elasticsearch import AsyncElasticsearch


class ElasticsearchClient:
    _client: AsyncElasticsearch = None

    @classmethod
    async def initialize(cls):
        if cls._client is None:
            hosts = settings.elasticsearch_hosts.split(",")
            cls._client = AsyncElasticsearch(hosts=hosts)

    @classmethod
    async def get_client(cls) -> AsyncElasticsearch:
        if cls._client is None:
            await cls.initialize()
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None
