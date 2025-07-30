"""
로컬 임베딩을 사용하는 PDF 처리 서비스
"""
import os
import re
import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter


def clean_java_text(text: str) -> str:
    """
    OCR 과정에서 깨지기 쉬운 Java 관련 텍스트를 정규식을 사용해 복원합니다.
    """
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


def remove_ebook_sample_text(text: str) -> str:
    """
    PDF에 포함된 eBook 샘플 관련 상용구를 제거합니다.
    """
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


class LocalPDFProcessingService:
    """로컬 임베딩을 사용하는 PDF 처리 서비스"""
    
    def __init__(self):
        # 로컬 임베딩 모델 로드
        self.embeddings = SentenceTransformer('all-MiniLM-L6-v2')
        print("✅ 로컬 임베딩 모델 로드 완료")
    
    def process_pdf_and_create_chunks(self, pdf_path: str, max_pages: Optional[int] = None) -> List[Document]:
        """
        PDF를 처리하고 청크를 생성합니다.
        
        Args:
            pdf_path: PDF 파일 경로
            max_pages: 처리할 최대 페이지 수 (테스트용)
            
        Returns:
            Document 리스트
        """
        print(f"📄 PDF 텍스트 추출 및 전처리 시작...")
        
        # PDF 텍스트 추출
        pages_content = self._extract_pdf_text(pdf_path)
        
        if max_pages:
            pages_content = pages_content[:max_pages]
            print(f"🧪 테스트 모드: {max_pages}개 페이지만 처리")
        
        if not pages_content:
            print("❌ PDF에서 유효한 텍스트를 추출하지 못했습니다.")
            return []
        
        print(f"✅ 전처리 완료! {len(pages_content)}개 페이지")
        
        # LangChain Document 형식으로 변환
        documents = []
        for page in pages_content:
            doc = Document(
                page_content=page['content'],
                metadata={
                    'page_number': page['page_number'],
                    'word_count': page['word_count'],
                    'source': pdf_path
                }
            )
            documents.append(doc)
        
        # RecursiveCharacterTextSplitter로 청킹 (OpenAI 의존성 없음)
        print("🔪 텍스트 청킹 시작...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        
        print(f"✅ 청킹 완료: {len(chunks)}개 청크")
        return chunks
    
    def _extract_pdf_text(self, pdf_path: str) -> list[dict]:
        """
        PDF 파일에서 텍스트를 추출하고 전처리를 수행합니다.
        """
        pages_content = []
        print(f"🔍 PDF 파일 경로: {pdf_path}")

        with fitz.open(pdf_path) as doc:
            print(f"📄 PDF 총 페이지 수: {len(doc)}")
            for page_num, page in enumerate(doc, 1):
                text = page.get_text()
                print(f"📖 페이지 {page_num}: 텍스트 길이 = {len(text.strip())}")
                
                if text and len(text.strip()) > 1:
                    # OCR 오류 수정 적용
                    corrected_text = clean_java_text(text)
                    # eBook 샘플 텍스트 제거
                    final_text = remove_ebook_sample_text(corrected_text)
                    
                    if final_text.strip():
                        pages_content.append({
                            'page_number': page_num,
                            'content': final_text,
                            'word_count': len(final_text.split())
                        })
                        print(f"✅ 페이지 {page_num} 처리 완료 (단어 수: {len(final_text.split())})")
                    else:
                        print(f"⚠️ 페이지 {page_num}: 최종 텍스트가 비어있음")
                else:
                    print(f"⚠️ 페이지 {page_num}: 텍스트가 너무 짧거나 없음")
                    
        # 최소 3페이지 이상의 유효한 텍스트가 있어야 처리 진행
        if len(pages_content) < 3:
            print(f"❌ 유효한 페이지가 너무 적습니다. (필요: 3개, 실제: {len(pages_content)}개)")
            return []
        
        print(f"📊 총 처리된 페이지: {len(pages_content)}개")
        return pages_content
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        텍스트 리스트를 임베딩으로 변환합니다.
        """
        return self.embeddings.encode(texts).tolist()
    
    def similarity_search(self, query: str, documents: List[Document], k: int = 5) -> List[Document]:
        """
        쿼리와 유사한 문서를 검색합니다.
        """
        if not documents:
            return []
        
        # 쿼리 임베딩 생성
        query_embedding = self.embeddings.encode([query])[0]
        
        # 문서 임베딩 생성
        doc_texts = [doc.page_content for doc in documents]
        doc_embeddings = self.embeddings.encode(doc_texts)
        
        # 코사인 유사도 계산
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
        
        # 유사도 순으로 정렬
        sorted_indices = similarities.argsort()[-k:][::-1]
        
        return [documents[i] for i in sorted_indices]


# 싱글톤 인스턴스
_local_pdf_service = None

def get_local_pdf_service():
    global _local_pdf_service
    if _local_pdf_service is None:
        _local_pdf_service = LocalPDFProcessingService()
    return _local_pdf_service 