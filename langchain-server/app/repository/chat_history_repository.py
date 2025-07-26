from datetime import datetime
from typing import List, Optional
from elasticsearch import Elasticsearch
from app.core.elasticsearch_client import es_client
from app.core.config import settings
from app.entity.chat_history import ChatHistory

print("[DEBUG] ChatHistoryRepository module loaded successfully!")

class ChatHistoryRepository:
    INDEX_NAME = "chat_history"

    def __init__(self):
        self.es_client: Elasticsearch = es_client
        self.index_name = self.INDEX_NAME
        print(f"[DEBUG] ChatHistoryRepository initialized with index: {self.index_name}")
    
    def create_index_if_not_exists(self):
        """인덱스가 존재하지 않으면 생성합니다."""
        if not self.es_client.indices.exists(index=self.index_name):
            mapping = {
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "korean_analyzer": {
                                "type": "custom",
                                "tokenizer": "nori_tokenizer",
                                "filter": ["lowercase", "trim", "nori_part_of_speech", "nori_readingform"]
                            }
                        }
                    }
                },
                "mappings": {
                    "properties": {
                        "age": {"type": "integer"},
                        "background": {"type": "keyword"},
                        "feedback": {
                            "type": "text",
                            "analyzer": "korean_analyzer",
                            "search_analyzer": "korean_analyzer"
                        },
                        "question": {
                            "type": "text",
                            "analyzer": "korean_analyzer",
                            "search_analyzer": "korean_analyzer"
                        },
                        "answer": {
                            "type": "text",
                            "analyzer": "korean_analyzer",
                            "search_analyzer": "korean_analyzer"
                        },
                        "created_at": {"type": "date"},
                        "model_name": {"type": "keyword"}
                    }
                }
            }
            self.es_client.indices.create(index=self.index_name, body=mapping)
    
    def save_chat_history(self, chat_history: ChatHistory) -> str:
        """채팅 이력을 Elasticsearch에 저장합니다."""
        self.create_index_if_not_exists()
        
        # 엔티티의 메서드를 사용하여 Elasticsearch 문서로 변환
        document = chat_history.to_elasticsearch_doc()
        
        response = self.es_client.index(
            index=self.index_name,
            body=document
        )
        
        return response['_id']
    
    def get_chat_history_by_id(self, history_id: str) -> Optional[ChatHistory]:
        """ID로 채팅 이력을 조회합니다."""
        try:
            response = self.es_client.get(
                index=self.index_name,
                id=history_id
            )
            
            # 엔티티의 클래스 메서드를 사용하여 생성
            return ChatHistory.from_elasticsearch_doc(
                response['_id'], 
                response['_source']
            )
        except Exception:
            return None
    
    def search_chat_history(self, query: str, size: int = 10) -> List[ChatHistory]:
        """채팅 이력을 검색합니다."""
        print(f"[DEBUG] Searching for query: '{query}' in index: {self.index_name}")
        
        # 더 간단한 검색 쿼리로 테스트
        search_body = {
            "query": {
                "match": {
                    "question": query
                }
            },
            "sort": [{"created_at": {"order": "desc"}}],
            "size": size
        }
        
        print(f"[DEBUG] Search body: {search_body}")
        
        try:
            response = self.es_client.search(
                index=self.index_name,
                body=search_body
            )
            print(f"[DEBUG] ES response hits total: {response['hits']['total']}")
            print(f"[DEBUG] ES response hits: {len(response['hits']['hits'])}")
            
            results = []
            for hit in response['hits']['hits']:
                # 엔티티의 클래스 메서드를 사용하여 생성
                chat_history = ChatHistory.from_elasticsearch_doc(
                    hit['_id'], 
                    hit['_source']
                )
                results.append(chat_history)
            
            print(f"[DEBUG] Final results count: {len(results)}")
            return results
            
        except Exception as e:
            print(f"[DEBUG] Search error: {e}")
            return []
    
    def get_all_chat_history(self, size: int = 100) -> List[ChatHistory]:
        """모든 채팅 이력을 조회합니다."""
        search_body = {
            "query": {"match_all": {}},
            "sort": [{"created_at": {"order": "desc"}}],
            "size": size
        }
        
        response = self.es_client.search(
            index=self.index_name,
            body=search_body
        )
        
        results = []
        for hit in response['hits']['hits']:
            # 엔티티의 클래스 메서드를 사용하여 생성
            chat_history = ChatHistory.from_elasticsearch_doc(
                hit['_id'], 
                hit['_source']
            )
            results.append(chat_history)
        
        return results
    
    def delete_chat_history(self, history_id: str) -> bool:
        """채팅 이력을 삭제합니다."""
        try:
            response = self.es_client.delete(
                index=self.index_name,
                id=history_id
            )
            return response['result'] == 'deleted'
        except Exception:
            return False
    
    def get_recent_chat_history(self, days: int = 7, size: int = 50) -> List[ChatHistory]:
        """최근 N일 내의 채팅 이력을 조회합니다."""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        search_body = {
            "query": {
                "range": {
                    "created_at": {
                        "gte": cutoff_date.isoformat()
                    }
                }
            },
            "sort": [{"created_at": {"order": "desc"}}],
            "size": size
        }
        
        response = self.es_client.search(
            index=self.index_name,
            body=search_body
        )
        
        results = []
        for hit in response['hits']['hits']:
            chat_history = ChatHistory.from_elasticsearch_doc(
                hit['_id'], 
                hit['_source']
            )
            results.append(chat_history)
        
        return results
    
    def get_chat_history_by_age_group(self, age_group: str, size: int = 50) -> List[ChatHistory]:
        """연령대별 채팅 이력을 조회합니다."""
        age_ranges = {
            "어린이": {"range": {"age": {"lt": 10}}},
            "청소년": {"range": {"age": {"gte": 10, "lt": 20}}},
            "20대": {"range": {"age": {"gte": 20, "lt": 30}}},
            "30대": {"range": {"age": {"gte": 30, "lt": 40}}},
            "40대": {"range": {"age": {"gte": 40, "lt": 50}}},
            "50대 이상": {"range": {"age": {"gte": 50}}}
        }
        
        if age_group not in age_ranges:
            return []
        
        search_body = {
            "query": age_ranges[age_group],
            "sort": [{"created_at": {"order": "desc"}}],
            "size": size
        }
        
        response = self.es_client.search(
            index=self.index_name,
            body=search_body
        )
        
        results = []
        for hit in response['hits']['hits']:
            chat_history = ChatHistory.from_elasticsearch_doc(
                hit['_id'], 
                hit['_source']
            )
            results.append(chat_history)
        
        return results

# 싱글톤 인스턴스
chat_history_repository = ChatHistoryRepository() 