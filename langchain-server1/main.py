"""
🚀 상태 머신 기반 Java Learning Chat System
ChatState enum을 사용한 상태 관리와 FastAPI 호출을 통한 기능 처리
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv("../.env")  # 상위 디렉토리의 .env 파일 로드

# LangChain 관련 임포트
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_experimental.text_splitter import SemanticChunker

# PyMuPDF 및 텍스트 전처리 관련 임포트
import fitz  # PyMuPDF
import re
import json

# 내부 모듈 임포트
from core.state_machine import ChatState, StateMachine, FastAPIClient
from core.models import ModelManager
from core.vector_store import VectorStoreManager
from core.chains import ChainFactory
from core.concept_explainer import ConceptExplainer
from utils.file_manager import ConfigManager, KeywordManager, AnswerHistoryManager
from generators.question_generator import QuestionGenerator
from analyzers.adaptive_learning import WeaknessAnalyzer, QuestionQualityAnalyzer

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

class JavaLearningSystem:
    """Java 학습 시스템 메인 클래스"""
    
    def __init__(self):
        print("🚀 **상태 머신 기반 Java Learning Chat System**")
        print("="*60)
        
        # 설정 및 데이터 매니저 초기화
        self.config_manager = ConfigManager()
        self.keyword_manager = KeywordManager()
        self.answer_history_manager = AnswerHistoryManager()
        
        # 핵심 컴포넌트들
        self.model_manager = ModelManager()
        self.vector_store_manager = None
        self.chain_manager = None
        self.chain_executor = None
        
        # 생성기 및 분석기들
        self.question_generator = None
        self.weakness_analyzer = None
        self.quality_analyzer = None
        
        # 상태 머신 및 FastAPI 클라이언트
        self.state_machine = StateMachine()
        self.fastapi_client = FastAPIClient()
        
        # 개념 설명기
        self.concept_explainer = None
        
        # 시스템 상태
        self.is_initialized = False
        
        # 키워드 데이터 로드
        self.keywords_data = self._load_keywords()
        
        # 챕터별 페이지 범위 정의 (1부터 시작)
        self.chapter_pages = {
            "Chapter1 - 변수": (30, 107),
            "Chapter2 - 연산자": (108, 157),
            "Chapter3 - 조건문과 반복문": (158, 205),
            "Chapter4 - 배열": (206, 253),
            "Chapter5 - 객체지향 프로그래밍 I": (254, 339)
        }
    
    def _load_keywords(self) -> List[Dict[str, Any]]:
        """키워드 파일을 로드합니다."""
        try:
            keywords_file = "keywords.json"
            if os.path.exists(keywords_file):
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    keywords = json.load(f)
                print(f"📂 파일 로드: keywords.json ({len(keywords)}개 키워드)")
                return keywords
            else:
                # 상위 디렉토리에서 찾기
                parent_keywords = "../langchain-server/대화테스트/keywords.json"
                if os.path.exists(parent_keywords):
                    with open(parent_keywords, 'r', encoding='utf-8') as f:
                        keywords = json.load(f)
                    print(f"📂 파일 로드: {parent_keywords} ({len(keywords)}개 키워드)")
                    return keywords
                else:
                    print("📂 파일 없음: keywords.json (기본값 사용)")
                    return []
        except Exception as e:
            print(f"⚠️ 키워드 로딩 오류: {e}")
            return []
    
    def initialize_system(self) -> bool:
        """시스템을 초기화합니다."""
        print("\n🔧 시스템 초기화 중...")
        
        # 1. AI 모델 초기화
        if not self.model_manager.initialize_models():
            return False
        
        # 2. PDF 경로 설정
        pdf_path = self._get_pdf_path()
        if not pdf_path:
            print("⚠️ PDF 파일이 설정되지 않았습니다.")
            return False
        
        # 3. PDF 및 벡터 스토어 설정
        if not self._setup_vector_store(pdf_path):
            return False
        
        # 4. 체인 시스템 초기화
        self._initialize_chains()
        
        # 5. 생성기 및 분석기 초기화
        self._initialize_generators()
        self._initialize_analyzers()
        
        # 6. 개념 설명기 초기화
        self.concept_explainer = ConceptExplainer(self.chain_executor, self.vector_store_manager)
        
        self.is_initialized = True
        print("✅ 시스템 초기화 완료!")
        return True
    
    def _get_pdf_path(self) -> Optional[str]:
        """PDF 경로를 가져옵니다."""
        # 1. config.json에서 설정된 경로 확인
        config_path = self.config_manager.get("pdf_path")
        if config_path and os.path.exists(config_path):
            return config_path
        
        # 2. 환경변수에서 확인
        env_path = os.environ.get("JAVA_PDF_PATH")
        if env_path and os.path.exists(env_path):
            return env_path
        
        # 3. 기본 위치들 확인
        default_paths = [
            "javajungsuk4_sample.pdf",
            "../javajungsuk4_sample.pdf",
            "./data/javajungsuk4_sample.pdf",
            "../data/javajungsuk4_sample.pdf",
            "../langchain-server/대화테스트/data/javajungsuk4_sample.pdf",
            "../ai/javajungsuk4_sample.pdf"
        ]
        
        for path in default_paths:
            if os.path.exists(path):
                return path
        
        return "/Users/david/Documents/study/KDT_BE12_Toy_Project/ai/javajungsuk4_sample.pdf"
    
    def _setup_vector_store(self, pdf_path: str) -> bool:
        """벡터 스토어를 설정합니다."""
        try:
            print("📄 PDF 텍스트 추출 및 전처리 시작...")
            
            # PyMuPDF를 사용한 전처리된 텍스트 추출
            pages_content = extract_preprocessed_pdf_text(pdf_path)
            
            if not pages_content:
                print("❌ PDF에서 유효한 텍스트를 추출하지 못했습니다.")
                return False
            
            print(f"✅ 전처리 완료! {len(pages_content)}개 페이지")
            
            # LangChain Document 형식으로 변환
            from langchain.schema import Document
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
            
            # 텍스트 분할 (더 작은 청크로 분할)
            # 올바른 설정
            text_splitter = SemanticChunker(
                self.model_manager.get_embeddings(),
                breakpoint_threshold_type="percentile",
                breakpoint_threshold_amount=95
            )
            chunks = text_splitter.split_documents(documents)
            
            # 벡터 스토어 생성
            self.vector_store_manager = VectorStoreManager(self.model_manager.get_embeddings())
            success = self.vector_store_manager.setup_vector_store(chunks, pdf_path)
            
            if success:
                print(f"✅ 벡터 스토어 설정 완료: {len(chunks)}개 청크")
                print(f"   - 원본 페이지: {len(pages_content)}개")
                print(f"   - 총 단어 수: {sum(page['word_count'] for page in pages_content)}개")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"❌ 벡터 스토어 설정 실패: {e}")
            return False
    
    def _initialize_chains(self):
        """체인 시스템을 초기화합니다."""
        retriever = self.vector_store_manager.get_retriever(
            k=self.config_manager.get("vector_store_k", 5)
        )
        
        self.chain_manager, self.chain_executor = ChainFactory.create_complete_chain_system(
            llm=self.model_manager.get_llm(),
            retriever=retriever
        )
    
    def _initialize_generators(self):
        """생성기들을 초기화합니다."""
        # retriever 가져오기
        retriever = self.vector_store_manager.get_retriever()
        self.question_generator = QuestionGenerator(self.model_manager.get_llm(), retriever)
    
    def _initialize_analyzers(self):
        """분석기들을 초기화합니다."""
        self.weakness_analyzer = WeaknessAnalyzer(self.chain_executor)
        self.quality_analyzer = QuestionQualityAnalyzer(self.chain_executor)
    
    def run(self):
        """메인 실행 루프"""
        if not self.is_initialized:
            if not self.initialize_system():
                print("❌ 시스템 초기화 실패")
                return
        
        # 초기 상태 설정
        self.state_machine.transition_to(ChatState.WAITING_USER_SELECT_FEATURE)
        
        while True:
            try:
                # 현재 상태에 따른 처리
                current_state = self.state_machine.current_state
                
                if current_state == ChatState.WAITING_USER_SELECT_FEATURE:
                    self._handle_feature_selection()
                elif current_state == ChatState.WAITING_PROBLEM_CRITERIA_SELECTION:
                    self._handle_problem_criteria_selection()
                elif current_state == ChatState.WAITING_PROBLEM_CONTEXT_INPUT:
                    self._handle_problem_context_input()
                elif current_state == ChatState.WAITING_USER_ANSWER:
                    self._handle_user_answer()
                elif current_state == ChatState.WAITING_CONCEPT_INPUT:
                    self._handle_concept_input()
                elif current_state == ChatState.WAITING_CONCEPT_RATING:
                    self._handle_concept_rating()
                elif current_state == ChatState.WAITING_REASON_FOR_LOW_RATING:
                    self._handle_low_rating_reason()
                elif current_state == ChatState.WAITING_KEYWORD_FOR_PAGE_SEARCH:
                    self._handle_page_search_keyword()
                elif current_state == ChatState.WAITING_NEXT_ACTION_AFTER_LEARNING:
                    self._handle_next_action_after_learning()
                else:
                    print(f"❌ 알 수 없는 상태: {current_state}")
                    self.state_machine.transition_to(ChatState.WAITING_USER_SELECT_FEATURE)
                    
            except KeyboardInterrupt:
                print("\n\n👋 사용자에 의해 중단되었습니다.")
                break
            except Exception as e:
                print(f"❌ 오류 발생: {e}")
                self.state_machine.transition_to(ChatState.WAITING_USER_SELECT_FEATURE)
    
    def _handle_feature_selection(self):
        """기능 선택을 처리합니다."""
        print("\n" + "="*60)
        print("🎯 **Java 학습 시스템**")
        print("="*60)
        print("1️⃣  예상문제 생성")
        print("2️⃣  학습보충 (개념 설명)")
        print("3️⃣  페이지 찾기")
        print("0️⃣  종료")
        print("="*60)
        
        choice = input("\n선택하세요: ").strip()
        
        if choice == '1':
            self.state_machine.transition_to(ChatState.WAITING_PROBLEM_CRITERIA_SELECTION)
            print("🤖 시스템: 문제 생성을 선택하셨습니다. 어떤 방식으로 문제를 생성하시겠습니까?")
            print("1. 챕터/페이지 선택")
            print("2. 특정 개념 선택")
        elif choice == '2':
            self.state_machine.transition_to(ChatState.WAITING_CONCEPT_INPUT)
            print("🤖 시스템: 학습보충을 선택하셨습니다. 설명을 원하는 개념을 입력해주세요.")
        elif choice == '3':
            self.state_machine.transition_to(ChatState.WAITING_KEYWORD_FOR_PAGE_SEARCH)
            print("🤖 시스템: 페이지 찾기를 선택하셨습니다. 찾고 싶은 키워드를 입력해주세요.")
        elif choice == '0':
            print("👋 시스템을 종료합니다.")
            sys.exit(0)
        else:
            print("❌ 잘못된 선택입니다. 1-3, 0 중에서 선택해주세요.")
    
    def _handle_problem_criteria_selection(self):
        """문제 생성 기준 선택을 처리합니다."""
        choice = input("\n선택하세요: ").strip()
        
        if choice == '1':
            self.state_machine.transition_to(ChatState.WAITING_PROBLEM_CONTEXT_INPUT)
            print("🤖 시스템: 챕터/페이지 선택을 선택하셨습니다. 챕터명 또는 페이지 범위를 입력해주세요.")
            print("예시: Chapter1 - 변수, 30-50페이지")
        elif choice == '2':
            self.state_machine.transition_to(ChatState.WAITING_PROBLEM_CONTEXT_INPUT)
            print("🤖 시스템: 특정 개념 선택을 선택하셨습니다. 문제를 생성할 개념을 입력해주세요.")
        else:
            print("❌ 잘못된 선택입니다.")
    
    def _handle_problem_context_input(self):
        """문제 컨텍스트 입력을 처리합니다."""
        user_input = input("\n입력해주세요: ").strip()
        
        if not user_input:
            print("❌ 입력을 해주세요.")
            return
        
        # 입력 검증 및 매핑
        processed_input = self._process_user_input(user_input)
        if not processed_input:
            print("❌ 올바른 챕터명이나 개념을 입력해주세요.")
            return
        
        # 상태 전환
        self.state_machine.transition_to(ChatState.GENERATING_QUESTION_WITH_RAG)
        
        # FastAPI 호출 시뮬레이션
        print("🔍 FastAPI 호출 시뮬레이션: RAG 기반 문제 생성")
        print(f"   - Context: {processed_input}")
        
        # 문제 생성
        question = self.question_generator.generate_question(processed_input)
        
        if question:
            # 상태 전환
            self.state_machine.transition_to(ChatState.QUESTION_PRESENTED_TO_USER)
            
            # 문제 표시
            print(f"\n🤖 시스템: 문제가 생성되었습니다 (품질: {question.get('quality_score', 0.5)}):")
            print(f"{question['question']}")
            for i, option in enumerate(question['options'], 1):
                print(f"{i}. {option}")
            print("정답을 선택해주세요 (1-4):")
            
            # 컨텍스트 저장
            self.state_machine.update_context("current_question", question)
            self.state_machine.update_context("previous_topic", user_input)
            
            # 상태 전환
            self.state_machine.transition_to(ChatState.WAITING_USER_ANSWER)
        else:
            print("❌ 문제 생성에 실패했습니다. 다시 시도해주세요.")
            self.state_machine.transition_to(ChatState.WAITING_PROBLEM_CONTEXT_INPUT)
    
    def _handle_user_answer(self):
        """사용자 답변을 처리합니다."""
        try:
            user_answer = int(input("\n입력해주세요: ").strip())
            
            if 1 <= user_answer <= 4:
                # 상태 전환
                self.state_machine.transition_to(ChatState.EVALUATING_ANSWER_AND_LOGGING)
                
                # 현재 문제 가져오기
                current_question = self.state_machine.get_context("current_question")
                if not current_question:
                    print("❌ 문제 정보를 찾을 수 없습니다.")
                    self.state_machine.transition_to(ChatState.WAITING_USER_SELECT_FEATURE)
                    return
                
                # 답변 평가
                correct_answer = current_question.get('correct_answer', 1)
                is_correct = (user_answer == correct_answer)
                
                if is_correct:
                    print("🎉 정답입니다!")
                    self.state_machine.transition_to(ChatState.WAITING_NEXT_ACTION_AFTER_LEARNING)
                else:
                    print(f"❌ 틀렸습니다. 정답은 {correct_answer}번입니다.")
                    print(f"📖 **설명:** {current_question.get('explanation', '')}")
                    
                    # 오답 시 개념 설명
                    self.state_machine.transition_to(ChatState.PRESENTING_CONCEPT_EXPLANATION)
                    
                    # 문제에서 핵심 키워드 추출
                    concept_keyword = self._extract_primary_keyword_from_question(current_question)
                    print(f"\n📚 **{concept_keyword} 개념 설명**")
                    print("="*40)
                    
                    # 구체적인 개념 설명 생성
                    explanation = self.concept_explainer.explain_concept(concept_keyword)
                    
                    if explanation:
                        print(f"\n📚 **{concept_keyword} 개념 설명**")
                        print("="*40)
                        print(explanation)
                    
                    self.state_machine.transition_to(ChatState.WAITING_CONCEPT_RATING)
                    print("\n설명이 도움이 되었나요? (1-5점):")
            else:
                print("❌ 1-4 사이의 숫자를 입력해주세요.")
        except ValueError:
            print("❌ 올바른 숫자를 입력해주세요.")
    
    def _handle_concept_input(self):
        """개념 입력을 처리합니다."""
        concept = input("\n입력해주세요: ").strip()
        
        if not concept:
            print("❌ 개념을 입력해주세요.")
            return
        
        # 상태 전환
        self.state_machine.transition_to(ChatState.PRESENTING_CONCEPT_EXPLANATION)
        
        # 개념 설명 생성
        explanation = self.concept_explainer.explain_concept(concept)
        
        if explanation:
            print(f"\n📚 **{concept} 개념 설명**")
            print("="*40)
            print(explanation)
            
            # 상태 전환
            self.state_machine.transition_to(ChatState.WAITING_CONCEPT_RATING)
            print("\n설명이 도움이 되었나요? (1-5점):")
        else:
            print("❌ 개념 설명 생성에 실패했습니다.")
            self.state_machine.transition_to(ChatState.WAITING_USER_SELECT_FEATURE)
    
    def _handle_concept_rating(self):
        """개념 설명 평가를 처리합니다."""
        try:
            rating = int(input("\n입력해주세요: ").strip())
            
            if 1 <= rating <= 5:
                if rating <= 3:
                    # 낮은 평가 시 이유 요청
                    self.state_machine.transition_to(ChatState.WAITING_REASON_FOR_LOW_RATING)
                    print("더 나은 설명을 위해 어떤 부분이 부족했는지 알려주세요.")
                else:
                    # 높은 평가 시 다음 액션
                    print("설명이 도움이 되었다니 기쁩니다!")
                    self.state_machine.transition_to(ChatState.WAITING_NEXT_ACTION_AFTER_LEARNING)
            else:
                print("❌ 1-5 사이의 숫자를 입력해주세요.")
        except ValueError:
            print("❌ 올바른 숫자를 입력해주세요.")
    
    def _handle_low_rating_reason(self):
        """낮은 평가 이유를 처리합니다."""
        reason = input("\n입력해주세요: ").strip()
        
        if not reason:
            print("❌ 이유를 입력해주세요.")
            return
        
        # 상태 전환
        self.state_machine.transition_to(ChatState.REEXPLAINING_CONCEPT)
        
        # 재설명 생성
        concept_keyword = self.state_machine.get_context("current_concept", "Java")
        reexplanation = self.concept_explainer.reexplain_concept(concept_keyword, reason)
        
        if reexplanation:
            print(f"\n📖 **보충 설명**")
            print("="*40)
            print(f"🔍 **사용자 피드백:** {reason}")
            print("\n📖 **개선된 설명:**")
            print(reexplanation)
            
            # 상태 전환
            self.state_machine.transition_to(ChatState.WAITING_CONCEPT_RATING)
            print("\n이 설명이 도움이 되었나요? (1-5점):")
        else:
            print("❌ 재설명 생성에 실패했습니다.")
            self.state_machine.transition_to(ChatState.WAITING_USER_SELECT_FEATURE)
    
    def _handle_page_search_keyword(self):
        """페이지 검색 키워드를 처리합니다."""
        keyword = input("\n입력해주세요: ").strip()
        
        if not keyword:
            print("❌ 키워드를 입력해주세요.")
            return
        
        # 상태 전환
        self.state_machine.transition_to(ChatState.PROCESSING_PAGE_SEARCH_RESULT)
        
        # 페이지 검색
        search_results = self._search_pages_by_keyword(keyword)
        
        if search_results:
            print(f"\n🔍 '{keyword}' 검색 결과 ({len(search_results)}개):")
            for i, result in enumerate(search_results, 1):
                print(f"  {i}. {result}")
        else:
            print("❌ 검색 결과가 없습니다.")
        
        # 상태 전환
        self.state_machine.transition_to(ChatState.WAITING_USER_SELECT_FEATURE)
    
    def _handle_next_action_after_learning(self):
        """학습 후 다음 액션을 처리합니다."""
        print("\n다음 중 선택해주세요:")
        print("1. 다음 문제 풀기")
        print("2. 다른 기능으로 돌아가기")
        
        choice = input("\n선택하세요: ").strip()
        
        if choice == '1':
            # 이전 토픽으로 문제 생성
            previous_topic = self.state_machine.get_context("previous_topic")
            if previous_topic:
                self.state_machine.transition_to(ChatState.WAITING_PROBLEM_CONTEXT_INPUT)
                print(f"🤖 시스템: '{previous_topic}'에 대한 다음 문제를 생성합니다.")
            else:
                self.state_machine.transition_to(ChatState.WAITING_PROBLEM_CONTEXT_INPUT)
                print("🤖 시스템: 새로운 문제를 생성합니다.")
        elif choice == '2':
            self.state_machine.transition_to(ChatState.WAITING_USER_SELECT_FEATURE)
        else:
            print("❌ 잘못된 선택입니다.")
    
    def _extract_primary_keyword_from_question(self, question: Dict[str, Any]) -> str:
        """문제에서 주요 키워드를 추출합니다."""
        question_text = question.get('question', '').lower()
        explanation_text = question.get('explanation', '').lower()
        
        # 문제와 설명에서 키워드 검색
        search_text = question_text + " " + explanation_text
        
        # 구체적인 Java 키워드들 (우선순위 순)
        java_keywords = [
            'do-while', 'while', 'for', 'if', 'switch',  # 제어문
            '배열', 'array', '2차원', '다차원',  # 배열
            '변수', '상수', '타입', '형변환',  # 변수
            '클래스', '객체', '인스턴스', '생성자',  # 객체지향
            '메서드', '함수', '오버로딩', '오버라이딩',  # 메서드
            '상속', '다형성', '캡슐화', '추상화',  # 객체지향 개념
            '예외', 'try', 'catch', 'finally',  # 예외처리
            '패키지', 'import', '접근제어자'  # 기타
        ]
        
        # 가장 구체적인 키워드부터 검색
        for keyword in java_keywords:
            if keyword in search_text:
                return keyword
        
        # 문제 텍스트에서 특정 패턴 검색
        if 'do-while' in search_text or 'do while' in search_text:
            return 'do-while'
        elif 'while' in search_text:
            return 'while'
        elif 'for' in search_text:
            return 'for'
        elif 'if' in search_text:
            return 'if'
        elif '배열' in search_text or 'array' in search_text:
            return '배열'
        elif '변수' in search_text:
            return '변수'
        
        # 챕터 정보에서 추출
        chapter = question.get('chapter', '')
        if chapter:
            if '조건문' in chapter or '반복문' in chapter:
                return '제어문'
            elif '배열' in chapter:
                return '배열'
            elif '변수' in chapter:
                return '변수'
            elif '객체' in chapter:
                return '객체지향'
        
        return "Java"
    
    def _search_pages_by_keyword(self, keyword: str) -> List[str]:
        """키워드로 페이지를 검색합니다."""
        try:
            if not self.keywords_data:
                print("⚠️ 키워드 데이터가 로드되지 않았습니다.")
                return []
            
            # 동적 검색 로직
            search_results = self._dynamic_keyword_search(keyword)
            
            if search_results:
                results = []
                for kw in search_results:
                    pages = kw['pages']
                    chapter = self._get_chapter_by_page(pages[0])
                    page_str = ", ".join(map(str, pages))
                    results.append(f"📖 {kw['word']} - 페이지 {page_str} (챕터: {chapter})")
                
                # 결과를 페이지 순으로 정렬
                results.sort(key=lambda x: int(x.split('페이지 ')[1].split()[0].split(',')[0]))
                return results
            else:
                # 유사한 키워드 제안
                suggestions = self._suggest_similar_keywords(keyword)
                if suggestions:
                    print(f"💡 유사한 키워드: {', '.join(suggestions[:5])}")
                return []
                
        except Exception as e:
            print(f"❌ 검색 실패: {e}")
            return []
    
    def _dynamic_keyword_search(self, keyword: str) -> List[Dict[str, Any]]:
        """동적 키워드 검색 로직"""
        keyword_lower = keyword.lower().strip()
        found_keywords = []
        
        # 검색 전략 정의 (우선순위 순)
        search_strategies = [
            self._exact_match_search,
            self._word_boundary_search,
            self._partial_match_search,
            self._fuzzy_match_search
        ]
        
        # 각 전략을 순서대로 시도
        for strategy in search_strategies:
            results = strategy(keyword_lower)
            if results:
                found_keywords = results
                break
        
        return found_keywords
    
    def _exact_match_search(self, keyword: str) -> List[Dict[str, Any]]:
        """정확한 일치 검색"""
        exact_matches = []
        for keyword_data in self.keywords_data:
            if keyword_data['word'].lower().strip() == keyword:
                exact_matches.append(keyword_data)
        return exact_matches
    
    def _word_boundary_search(self, keyword: str) -> List[Dict[str, Any]]:
        """단어 경계 검색 (공백으로 구분된 단어)"""
        boundary_matches = []
        for keyword_data in self.keywords_data:
            word = keyword_data['word'].lower().strip()
            # 단어 경계에서 일치하는지 확인
            if (keyword == word or 
                word.startswith(keyword + ' ') or 
                word.endswith(' ' + keyword) or
                ' ' + keyword + ' ' in word):
                boundary_matches.append(keyword_data)
        return boundary_matches
    
    def _partial_match_search(self, keyword: str) -> List[Dict[str, Any]]:
        """부분 일치 검색"""
        partial_matches = []
        for keyword_data in self.keywords_data:
            word = keyword_data['word'].lower().strip()
            if keyword in word or word in keyword:
                partial_matches.append(keyword_data)
        return partial_matches
    
    def _fuzzy_match_search(self, keyword: str) -> List[Dict[str, Any]]:
        """유사도 기반 검색"""
        fuzzy_matches = []
        for keyword_data in self.keywords_data:
            word = keyword_data['word'].lower().strip()
            # 간단한 유사도 계산 (공통 문자 수)
            common_chars = sum(1 for c in keyword if c in word)
            similarity = common_chars / max(len(keyword), len(word))
            if similarity > 0.6:  # 60% 이상 유사
                fuzzy_matches.append(keyword_data)
        return fuzzy_matches
    
    def _suggest_similar_keywords(self, keyword: str) -> List[str]:
        """유사한 키워드를 제안합니다."""
        try:
            suggestions = []
            keyword_lower = keyword.lower()
            
            for keyword_data in self.keywords_data:
                word = keyword_data['word'].lower()
                # 부분 일치나 유사한 패턴 찾기
                if (keyword_lower in word or 
                    word in keyword_lower or 
                    any(char in word for char in keyword_lower if char.isalpha())):
                    suggestions.append(keyword_data['word'])
            
            return suggestions[:10]  # 최대 10개 제안
        except Exception:
            return []
    
    def _process_user_input(self, user_input: str) -> Optional[str]:
        """사용자 입력을 처리하고 적절한 챕터명으로 변환합니다."""
        input_lower = user_input.lower().strip()
        
        # 숫자 입력 처리 (챕터 번호)
        if input_lower.isdigit():
            chapter_num = int(input_lower)
            chapter_mapping = {
                1: "Chapter1 - 변수",
                2: "Chapter2 - 연산자", 
                3: "Chapter3 - 조건문과 반복문",
                4: "Chapter4 - 배열",
                5: "Chapter5 - 객체지향 프로그래밍 I"
            }
            if chapter_num in chapter_mapping:
                return chapter_mapping[chapter_num]
            else:
                print(f"❌ 챕터 {chapter_num}은 존재하지 않습니다. (1-5)")
                return None
        
        # 키워드 기반 매핑
        keyword_mapping = {
            "변수": "Chapter1 - 변수",
            "매개변수": "Chapter5 - 객체지향 프로그래밍 I",
            "parameter": "Chapter5 - 객체지향 프로그래밍 I",
            "연산자": "Chapter2 - 연산자",
            "조건문": "Chapter3 - 조건문과 반복문",
            "반복문": "Chapter3 - 조건문과 반복문",
            "for": "Chapter3 - 조건문과 반복문",
            "if": "Chapter3 - 조건문과 반복문",
            "while": "Chapter3 - 조건문과 반복문",
            "배열": "Chapter4 - 배열",
            "객체": "Chapter5 - 객체지향 프로그래밍 I",
            "클래스": "Chapter5 - 객체지향 프로그래밍 I",
            "상속": "Chapter5 - 객체지향 프로그래밍 I"
        }
        
        for keyword, chapter in keyword_mapping.items():
            if keyword in input_lower:
                return chapter
        
        # 정확한 챕터명인 경우
        for chapter_name in self.chapter_pages.keys():
            if chapter_name.lower() in input_lower or input_lower in chapter_name.lower():
                return chapter_name
        
        # 입력이 그대로 유효한 경우 (개념 설명용)
        return user_input
    
    def _get_chapter_by_page(self, page: int) -> str:
        """페이지 번호로 챕터를 찾습니다."""
        for chapter_name, (start, end) in self.chapter_pages.items():
            if start <= page <= end:
                return chapter_name
        return "알 수 없는 챕터"

def main():
    """메인 함수"""
    system = JavaLearningSystem()
    system.run()

if __name__ == "__main__":
    main() 