"""
향상된 RAG 서비스 - langchain-server1 기반
"""

import os
import re
import json
import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional, Tuple
from langchain.schema import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker
from app.core.vector_store import VectorStoreManager
from app.generators.question_generator import QuestionGenerator

class EnhancedRAGService:
    """향상된 RAG 서비스"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=2000
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="text-embedding-004"
        )
        self.vector_store_manager = VectorStoreManager(self.embeddings)
        self.question_generator = QuestionGenerator(self.llm)
        self.current_chunks = []
        
    def clean_java_text(self, text: str) -> str:
        """OCR 과정에서 깨지기 쉬운 Java 관련 텍스트를 정규식을 사용해 복원합니다."""
        patterns = [
            # 1. 예제 번호 복원 (▼ 기호 유무에 관계없이 처리)
            (r'▼?\s*예제\s+(\d+)\s*-\s*(\d+)\s*/\s*(\w+)\s*\.\s*j(?:ava)?\s*(?=[^\w]|$)', r'▼ 예제 \1-\2/\3.java'),
            
            # 2. 'FileName.java'와 같은 파일명 패턴 복원
            (r'(\w+)\s*\.\s*j(?:ava)?\s*(?=[^\w]|$)', r'\1.java'),
            
            # 3. 'ClassEx.java', 'ClassTest.java' 같은 클래스명 복원
            (r'(\w+(?:Ex|Test))\s*\.\s*j(?:ava)?\s*(?=[^\w]|$)', r'\1.java'),
            
            # 4. 'java.util', 'java.io' 같은 패키지명 복원
            (r'\b(j)\s*\.\s*(util|io|awt)\b', r'java.\2'),
            
            # 5. 'Java API' 같은 API 관련 용어 복원
            (r'\bJava\s+A\s*P\s*I\b', r'Java API'),
            
            # 6. System.out.print/println 구문 복원
            (r'System\s*\.\s*o[u\s]*t\s*\.\s*print(ln)?', r'System.out.print\1'),
            
            # 7. Java 기본 타입 키워드 복원
            (r'\b[fF]+[oOaA]*[tT]+\b', r'float'),
            (r'\b[iI]+[nN]*[tT]+\b', r'int'),
            (r'\b[dD]+[oO]*[uU]+[bB]+[lL]+[eE]+\b', r'double'),
            (r'\b[cC]+[hH]*[aA]+[rR]+\b', r'char'),
            (r'\b[bB]+[oO]*[lL]+[eEaA]*[nN]+\b', r'boolean'),
        ]
        
        cleaned = text
        for pattern, replacement in patterns:
            try:
                cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
            except re.error as e:
                print(f"Regex error for pattern '{pattern}': {e}")
                continue
        
        return cleaned
    
    def remove_ebook_sample_text(self, text: str) -> str:
        """PDF에 포함된 eBook 샘플 관련 상용구를 제거합니다."""
        patterns = [
            r"[ebook.*?샘플.*?무료.*?공유].*?seong\.namkung@gmail\.com",
            r"seong\.namkung@gmail\.com",
            r"2025\.\s*7\.\s*7\s*출시",
            r"올컬러.*?2025",
        ]
        
        cleaned_text = text
        for pattern in patterns:
            cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.DOTALL)
        
        return cleaned_text
    
    def extract_preprocessed_pdf_text(self, pdf_path: str, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """PDF에서 전처리된 텍스트를 추출합니다."""
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            if max_pages:
                pages_to_process = min(max_pages, total_pages)
            else:
                pages_to_process = total_pages
            
            print(f"📄 PDF 총 페이지 수: {total_pages}")
            print(f"🧪 테스트 모드: {pages_to_process}개 페이지만 처리")
            
            text_blocks = []
            
            for page_num in range(pages_to_process):
                page = doc[page_num]
                text = page.get_text()
                
                if not text.strip():
                    continue
                
                # 텍스트 정제
                cleaned_text = self.clean_java_text(text)
                cleaned_text = self.remove_ebook_sample_text(cleaned_text)
                
                if len(cleaned_text.strip()) > 50:  # 최소 길이 체크
                    text_blocks.append({
                        "page": page_num + 1,
                        "content": cleaned_text,
                        "word_count": len(cleaned_text.split())
                    })
                    print(f"✅ 페이지 {page_num + 1} 처리 완료 (단어 수: {len(cleaned_text.split())})")
            
            doc.close()
            return text_blocks
            
        except Exception as e:
            print(f"❌ PDF 처리 중 오류: {e}")
            return []
    
    def create_chunks_from_text_blocks(self, text_blocks: List[Dict[str, Any]]) -> List[Document]:
        """텍스트 블록을 청크로 분할합니다."""
        try:
            # SemanticChunker 사용
            chunker = SemanticChunker(self.embeddings)
            
            all_text = "\n\n".join([block["content"] for block in text_blocks])
            chunks = chunker.split_text(all_text)
            
            # Document 객체로 변환
            documents = []
            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": "java_textbook",
                        "chunk_id": i,
                        "total_chunks": len(chunks)
                    }
                )
                documents.append(doc)
            
            print(f"✅ 청킹 완료: {len(documents)}개 청크")
            return documents
            
        except Exception as e:
            print(f"❌ 청킹 중 오류: {e}")
            return []
    
    def setup_rag_system(self, pdf_path: str, max_pages: Optional[int] = None) -> Tuple[bool, str]:
        """RAG 시스템을 설정합니다."""
        try:
            # 1. PDF 텍스트 추출 및 전처리
            print(f"📄 PDF 텍스트 추출 및 전처리 시작...")
            text_blocks = self.extract_preprocessed_pdf_text(pdf_path, max_pages)
            
            if not text_blocks:
                return False, "PDF에서 유효한 텍스트를 추출하지 못했습니다."
            
            # 2. 청킹
            print(f"🔪 텍스트 청킹 시작...")
            chunks = self.create_chunks_from_text_blocks(text_blocks)
            
            if not chunks:
                return False, "텍스트 청킹에 실패했습니다."
            
            # 3. 벡터 스토어 설정 (직접 처리)
            try:
                from langchain_community.vectorstores import ElasticsearchStore
                
                # Elasticsearch 연결 설정 (Docker 환경)
                es_url = "http://elasticsearch:9200"
                index_name = "java_learning_docs"
                
                # Elasticsearch 벡터 스토어 생성
                self.vector_store_manager.vector_store = ElasticsearchStore.from_documents(
                    documents=chunks,
                    embedding=self.embeddings,
                    es_url=es_url,
                    index_name=index_name
                )
                
                print(f"✅ Elasticsearch 벡터 스토어 설정 완료: {index_name}")
                
            except Exception as e:
                print(f"❌ Elasticsearch 벡터 스토어 설정 실패: {e}")
                return False, f"벡터 스토어 설정에 실패했습니다: {str(e)}"
            
            # 4. 검색기 설정
            retriever = self.vector_store_manager.get_retriever(k=5)
            if retriever:
                self.question_generator.retriever = retriever
            
            self.current_chunks = chunks
            return True, f"RAG 시스템 설정 완료. {len(chunks)}개 청크 처리됨."
            
        except Exception as e:
            return False, f"RAG 시스템 설정 중 오류: {str(e)}"
    
    def generate_question(self, topic: str, difficulty: str = "보통") -> Optional[Dict[str, Any]]:
        """주제와 난이도를 바탕으로 문제를 생성합니다."""
        if not self.question_generator.retriever:
            print("❌ 검색기가 설정되지 않았습니다.")
            return None
        
        return self.question_generator.generate_question(topic, difficulty)
    
    def search_relevant_content(self, query: str, k: int = 5) -> List[Document]:
        """관련 내용을 검색합니다."""
        return self.vector_store_manager.similarity_search(query, k)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """처리 통계를 반환합니다."""
        return {
            "total_chunks": len(self.current_chunks),
            "vector_store_ready": self.vector_store_manager.vector_store is not None,
            "retriever_ready": self.question_generator.retriever is not None
        }

# 싱글톤 인스턴스
enhanced_rag_service = EnhancedRAGService() 