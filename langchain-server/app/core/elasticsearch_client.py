from app.core.config import settings
from elasticsearch import Elasticsearch


def create_elasticsearch_client():
    hosts = settings.elasticsearch_hosts.split(",")
    return Elasticsearch(hosts=hosts)


es_client = create_elasticsearch_client()
