"""
벡터 스토어 관리 (Elasticsearch)
"""

from typing import List, Optional
from langchain_community.vectorstores import ElasticsearchStore
from langchain.schema import Document

class VectorStoreManager:
    """Elasticsearch 벡터 스토어 관리 클래스"""
    
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.vector_store = None
        self.index_name = "java_learning_docs"
    
    def setup_vector_store(self, chunks: List[Document], pdf_path: str) -> bool:
        """Elasticsearch 벡터 스토어를 설정합니다."""
        try:
            # Elasticsearch 연결 설정
            es_url = "http://localhost:9200"
            
            # Elasticsearch 벡터 스토어 생성
            self.vector_store = ElasticsearchStore.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                es_url=es_url,
                index_name=self.index_name
            )
            
            print(f"✅ Elasticsearch 벡터 스토어 설정 완료: {self.index_name}")
            return True
            
        except Exception as e:
            print(f"❌ Elasticsearch 벡터 스토어 설정 실패: {e}")
            return False
    
    def get_retriever(self, k: int = 5):
        """검색기를 반환합니다."""
        if self.vector_store:
            return self.vector_store.as_retriever(search_kwargs={"k": k})
        return None
    
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        """유사도 검색을 수행합니다."""
        if self.vector_store:
            return self.vector_store.similarity_search(query, k=k)
        return [] 