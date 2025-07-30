"""
RAG (Retrieval-Augmented Generation) 공통 서비스
"""

import os
from dotenv import load_dotenv
import base64
import tempfile
import os
import time
from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import ElasticsearchStore
from app.services.pdf_service import pdf_service
from app.services.cache_service import cache_service

# 환경 변수 로드
load_dotenv('../.env.prod')
load_dotenv('.env.prod')
load_dotenv('.env')

class RAGService:
    """RAG 공통 서비스"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=2000
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001"
        )
        self.vector_store = None
        self.current_chunks = []
    
    def process_pdf_and_setup_rag(self, pdf_base64: str, max_pages: Optional[int] = None) -> Tuple[bool, str]:
        """
        PDF를 처리하고 RAG 시스템을 설정합니다.
        
        Args:
            pdf_base64: Base64로 인코딩된 PDF 데이터
            max_pages: 처리할 최대 페이지 수
            
        Returns:
            (성공여부, 메시지)
        """
        temp_file_path = None
        try:
            # 1. Base64를 PDF 파일로 변환
            pdf_data = base64.b64decode(pdf_base64)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_data)
                temp_file_path = temp_file.name
            
            # 2. PDF 처리 및 청킹
            pdf_service_instance = pdf_service()
            chunks = pdf_service_instance.process_pdf_and_create_chunks(
                temp_file_path,
                max_pages=max_pages
            )
            
            if not chunks:
                return False, "PDF 처리에 실패했습니다."
            
            # 3. 벡터 스토어 설정
            success = self._setup_vector_store(chunks)
            if not success:
                return False, "벡터 스토어 설정에 실패했습니다."
            
            self.current_chunks = chunks
            return True, f"RAG 시스템 설정 완료. {len(chunks)}개 청크 처리됨."
            
        except Exception as e:
            return False, f"PDF 처리 중 오류 발생: {str(e)}"
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
    
    def process_pdf_and_setup_rag_from_file(self, pdf_path: str, max_pages: Optional[int] = None) -> Tuple[bool, str]:
        """
        PDF 파일을 직접 처리하고 RAG 시스템을 설정합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            max_pages: 처리할 최대 페이지 수
            
        Returns:
            (성공여부, 메시지)
        """
        try:
            # 1. PDF 처리 및 청킹
            pdf_service_instance = pdf_service()
            chunks = pdf_service_instance.process_pdf_and_create_chunks(
                pdf_path,
                max_pages=max_pages
            )
            
            if not chunks:
                return False, "PDF 처리에 실패했습니다."
            
            # 2. 벡터 스토어 설정
            success = self._setup_vector_store(chunks)
            if not success:
                return False, "벡터 스토어 설정에 실패했습니다."
            
            self.current_chunks = chunks
            return True, f"RAG 시스템 설정 완료. {len(chunks)}개 청크 처리됨."
            
        except Exception as e:
            return False, f"PDF 처리 중 오류 발생: {str(e)}"
    
    def _setup_vector_store(self, chunks: List[Document], index_name: str = "java_learning_docs") -> bool:
        """벡터 스토어를 설정합니다."""
        try:
            self.vector_store = ElasticsearchStore.from_documents(
                documents=chunks,
                embedding=self.embeddings,
                es_url="http://elasticsearch:9200",
                index_name=index_name
            )
            print(f"✅ Elasticsearch 벡터 스토어 설정 완료: {index_name}")
            return True
        except Exception as e:
            print(f"❌ Elasticsearch 벡터 스토어 설정 실패: {e}")
            return False
    
    def search_relevant_chunks(self, query: str, k: int = 5) -> List[Document]:
        """
        쿼리와 관련된 청크를 검색합니다.
        
        Args:
            query: 검색 쿼리
            k: 검색할 청크 수
            
        Returns:
            관련 문서 리스트
        """
        if not self.vector_store:
            return []
        
        try:
            docs = self.vector_store.similarity_search(query, k=k)
            return docs
        except Exception as e:
            print(f"❌ 청크 검색 실패: {e}")
            return []
    
    def generate_rag_response(self, query: str, context: str, prompt_template: str) -> str:
        """
        RAG를 사용하여 응답을 생성합니다.
        
        Args:
            query: 사용자 쿼리
            context: 관련 컨텍스트
            prompt_template: 프롬프트 템플릿
            
        Returns:
            생성된 응답
        """
        try:
            full_prompt = prompt_template.format(
                query=query,
                context=context
            )
            
            response = self.llm.invoke(full_prompt)
            return response.content
            
        except Exception as e:
            print(f"❌ RAG 응답 생성 실패: {e}")
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """처리 통계를 반환합니다."""
        return {
            "chunks_count": len(self.current_chunks),
            "vector_store_ready": self.vector_store is not None,
            "embeddings_ready": self.embeddings is not None,
            "llm_ready": self.llm is not None
        }


# 싱글톤 인스턴스
rag_service = RAGService() 