"""
PDF 처리 서비스
"""
import os
import re
import fitz
from typing import List, Dict, Tuple, Optional
from langchain.schema import Document
from app.services.cache_service import cache_service
from app.core.logging_config import get_logger

logger = get_logger(__name__)
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
        """라인별로 불필요한 내용을 정리합니다."""
        line = line.strip()
        if not line:
            return ""
        
        # 더 관대한 조건: 2글자 이상이면 유지
        if len(line) < 2:
            return ""
        
        for pattern in self.remove_line_patterns:
            if re.match(pattern, line):
                return ""
        
        # 특수문자만 있는 라인 제거 (더 관대하게)
        if re.match(r'^[^\w\s가-힣]+$', line) and len(line) < 5:
            return ""
        
        return line

    def is_code_block(self, text: str) -> bool:
        """Java 코드 블록인지 추정합니다."""
        code_indicators = ['class ', 'public ', 'static ', 'void ', 'import ', '//', '/*', '{', '}', ';']
        return any(indicator in text for indicator in code_indicators)

    def is_table_block(self, lines: list[str]) -> bool:
        """여러 줄로 구성된 텍스트 블록이 표인지 추정합니다."""
        if len(lines) < 2:
            return False
        
        full_text = '\n'.join(lines)
        for pattern in self.table_content_patterns:
            if re.search(pattern, full_text, re.DOTALL):
                return True
        
        # 대부분의 라인이 짧고(70% 이상), 숫자 포함 라인이 절반 이상이면 표로 간주
        short_lines = sum(1 for line in lines if len(line.strip()) < 20)
        numeric_lines = sum(1 for line in lines if re.search(r'\d', line))
        if len(lines) > 0 and short_lines / len(lines) > 0.7 and numeric_lines / len(lines) > 0.5:
            return True
        
        return False

    def is_valid_content_block(self, block_text: str) -> bool:
        """유효한 콘텐츠(코드 또는 설명)를 담고 있는 텍스트 블록인지 판단합니다."""
        if not block_text.strip():
            return False
        
        lines = block_text.split('\n')
        if self.is_table_block(lines):
            return False
        
        # 더 관대한 조건: 한글이 있거나, 코드의 일부이거나, 영어 문장이 있으면 유효한 블록으로 간주
        if re.search(r'[가-힣]', block_text) or self.is_code_block(block_text):
            return True
        
        # 영어 문장이 있는지 확인 (더 관대하게)
        sentences = re.split(r'[.!?]', block_text)
        return any(len(s.strip()) > 5 for s in sentences if s.strip())


def sort_blocks_by_reading_order(text_blocks: list) -> list:
    """PyMuPDF 텍스트 블록을 읽기 순서(위->아래, 왼쪽->오른쪽)로 정렬합니다."""
    # 텍스트 블록(type=0)만 필터링
    text_only_blocks = [b for b in text_blocks if b[6] == 0]
    # y좌표(b[1]) 우선, 같은 라인이면 x좌표(b[0]) 순으로 정렬
    return sorted(text_only_blocks, key=lambda b: (b[1], b[0]))


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
            if 1 <= page_num <= 52:
                continue
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
        from app.core.config import settings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.openai_api_key
        )
    
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
            logger.warning("PDF에서 유효한 텍스트를 추출하지 못했습니다.")
            return []
        
        logger.info(f"전처리 완료! {len(pages_content)}개 페이지")
        
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
        
        logger.info(f"청킹 완료: {len(chunks)}개 청크")
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