from elasticsearch import Elasticsearch
from app.core.config import settings

def create_elasticsearch_client():
    hosts = settings.elasticsearch_hosts.split(',')
    return Elasticsearch(hosts=hosts)

es_client = create_elasticsearch_client()
