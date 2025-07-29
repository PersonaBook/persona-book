"""
PDF 처리 서비스
"""
import os
import re
import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings


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


class JavaTextbookCleaner:
    """
    Java 교재 PDF에서 추출된 텍스트를 정제하는 클래스.
    """
    def __init__(self):
        # 제거할 라인 패턴
        self.remove_line_patterns = [
            r'^\s*[\|\-\+\s]+$',
            r'^\s*[\d\s\.\,\|\-]+\s*$',
            r'^\s*Chapter\s+\d+\s*$',
            r'^\s*[><]?\s*\d+\s*[><]?$',
        ]
        # 표의 내용으로 판단되는 키워드 패턴
        self.table_content_patterns = [
            r'종\s*류.*?연산자.*?우선순위',
            r'결합규칙.*?연산자',
            r'우선순위.*?높음.*?낮음',
        ]
    
    def clean_line(self, line: str) -> str:
        """라인을 정제합니다."""
        # 제거할 패턴에 해당하는 라인 제거
        for pattern in self.remove_line_patterns:
            if re.match(pattern, line):
                return ""
        
        # 앞뒤 공백 제거
        return line.strip()
    
    def is_code_block(self, text: str) -> bool:
        """코드 블록인지 판단합니다."""
        code_indicators = ['public', 'class', 'void', 'main', 'System.out', 'import', 'package']
        return any(indicator in text for indicator in code_indicators)
    
    def is_table_block(self, lines: list[str]) -> bool:
        """표 블록인지 판단합니다."""
        text = '\n'.join(lines)
        return any(re.search(pattern, text) for pattern in self.table_content_patterns)
    
    def is_valid_content_block(self, block_text: str) -> bool:
        """유효한 콘텐츠 블록인지 판단합니다."""
        if not block_text or len(block_text.strip()) < 10:
            return False
        
        # 코드 블록이나 표 블록은 유효
        if self.is_code_block(block_text):
            return True
        
        lines = block_text.splitlines()
        if self.is_table_block(lines):
            return True
        
        # 일반 텍스트는 최소 길이 확인
        return len(block_text.strip()) >= 20


def sort_blocks_by_reading_order(text_blocks: list) -> list:
    """PyMuPDF 텍스트 블록을 읽기 순서(위->아래, 왼쪽->오른쪽)로 정렬합니다."""
    def get_block_position(block):
        # block[0]: x0, block[1]: y0, block[2]: x1, block[3]: y1
        return (block[1], block[0])  # (y, x) 순서로 정렬
    
    return sorted(text_blocks, key=get_block_position)


def extract_preprocessed_pdf_text(pdf_path: str) -> list[dict]:
    """
    PDF 파일에서 텍스트를 추출하고 전처리를 수행합니다.
    
    Args:
        pdf_path: 처리할 PDF 파일의 경로

    Returns:
        페이지별로 정리된 텍스트 정보를 담은 딕셔너리 리스트
    """
    cleaner = JavaTextbookCleaner()
    pages_content = []

    with fitz.open(pdf_path) as doc:
        for page_num, page in enumerate(doc, 1):
            text_blocks = page.get_text("blocks")
            sorted_blocks = sort_blocks_by_reading_order(text_blocks)
            
            page_content = []
            for block in sorted_blocks:
                block_text = block[4]
                if cleaner.is_valid_content_block(block_text):
                    cleaned_lines = [cleaner.clean_line(line) for line in block_text.splitlines()]
                    cleaned_block = '\n'.join(filter(None, cleaned_lines))
                    if cleaned_block:
                        # OCR 오류 수정 적용
                        corrected_text = clean_java_text(cleaned_block)
                        # eBook 샘플 텍스트 제거
                        final_text = remove_ebook_sample_text(corrected_text)
                        page_content.append(final_text)
            
            if page_content:
                full_text = "\n\n".join(page_content)
                pages_content.append({
                    'page_number': page_num,
                    'content': full_text,
                    'word_count': len(full_text.split())
                })
    
    return pages_content


class PDFProcessingService:
    """PDF 처리 서비스"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
    
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
        pages_content = extract_preprocessed_pdf_text(pdf_path)
        
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
        
        # SemanticChunker로 청킹
        print("🔪 의미적 청킹 시작...")
        text_splitter = SemanticChunker(
            self.embeddings,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=70
        )
        chunks = text_splitter.split_documents(documents)
        
        print(f"✅ 청킹 완료: {len(chunks)}개 청크")
        return chunks


# 싱글톤 인스턴스 (지연 초기화)
_pdf_service = None

def get_pdf_service():
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFProcessingService()
    return _pdf_service

# 기존 호환성을 위한 별칭
pdf_service = get_pdf_service 