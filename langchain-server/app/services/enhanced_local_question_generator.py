"""
향상된 로컬 임베딩을 사용하는 문제 생성 서비스
"""
import os
import json
import random
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from app.services.local_pdf_service import get_local_pdf_service


class EnhancedLocalQuestionGeneratorService:
    """향상된 로컬 임베딩을 사용하는 문제 생성 서비스"""
    
    def __init__(self):
        self.local_pdf_service = get_local_pdf_service()
        self.documents = []
        
        # 챕터별 페이지 범위 정의 (1부터 시작)
        self.chapter_pages = {
            "Chapter2 - 변수": (30, 107),
            "Chapter3 - 연산자": (108, 157),
            "Chapter4 - 조건문과 반복문": (158, 205),
            "Chapter5 - 배열": (206, 253),
            "Chapter6 - 객체지향 프로그래밍 I": (254, 339)
        }
        
        # 키워드 데이터 로드
        self.keywords_data = self._load_keywords()
        
        # 챕터별 문제 템플릿
        self.chapter_question_templates = {
            "Chapter2 - 변수": [
                {
                    "question": "Java에서 변수 선언 시 기본값이 자동으로 할당되는 것은?",
                    "options": [
                        "A) 지역 변수",
                        "B) 인스턴스 변수", 
                        "C) 매개변수",
                        "D) 모든 변수"
                    ],
                    "answer": "B) 인스턴스 변수",
                    "explanation": "인스턴스 변수는 객체가 생성될 때 기본값이 자동으로 할당됩니다. 지역 변수는 반드시 초기화해야 합니다."
                },
                {
                    "question": "다음 중 Java의 기본형이 아닌 것은?",
                    "options": [
                        "A) int",
                        "B) double", 
                        "C) String",
                        "D) boolean"
                    ],
                    "answer": "C) String",
                    "explanation": "String은 참조형입니다. int, double, boolean은 기본형입니다."
                }
            ],
            "Chapter3 - 연산자": [
                {
                    "question": "다음 중 산술 연산자가 아닌 것은?",
                    "options": [
                        "A) +",
                        "B) -", 
                        "C) =",
                        "D) *"
                    ],
                    "answer": "C) =",
                    "explanation": "=는 대입 연산자입니다. +, -, *는 산술 연산자입니다."
                },
                {
                    "question": "Java에서 나머지 연산자(%)의 결과는?",
                    "options": [
                        "A) 항상 양수",
                        "B) 항상 음수", 
                        "C) 피연산자의 부호를 따름",
                        "D) 항상 0"
                    ],
                    "answer": "C) 피연산자의 부호를 따름",
                    "explanation": "나머지 연산자의 결과는 왼쪽 피연산자의 부호를 따릅니다."
                }
            ],
            "Chapter4 - 조건문과 반복문": [
                {
                    "question": "Java에서 쓰레드를 생성하는 방법 중 올바른 것은?",
                    "options": [
                        "A) Thread 클래스만 사용",
                        "B) Runnable 인터페이스만 사용", 
                        "C) Thread 클래스와 Runnable 인터페이스 모두 사용 가능",
                        "D) Thread 클래스는 사용할 수 없음"
                    ],
                    "answer": "C) Thread 클래스와 Runnable 인터페이스 모두 사용 가능",
                    "explanation": "Java에서는 Thread 클래스를 상속받거나 Runnable 인터페이스를 구현하여 쓰레드를 생성할 수 있습니다."
                },
                {
                    "question": "다음 중 쓰레드의 상태가 아닌 것은?",
                    "options": [
                        "A) NEW",
                        "B) RUNNABLE", 
                        "C) WAITING",
                        "D) FINISHED"
                    ],
                    "answer": "D) FINISHED",
                    "explanation": "Java 쓰레드의 상태는 NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED입니다. FINISHED는 존재하지 않습니다."
                },
                {
                    "question": "for문의 초기화, 조건식, 증감식 중 가장 먼저 실행되는 것은?",
                    "options": [
                        "A) 초기화",
                        "B) 조건식", 
                        "C) 증감식",
                        "D) 실행문"
                    ],
                    "answer": "A) 초기화",
                    "explanation": "for문은 초기화 → 조건식 → 실행문 → 증감식 순서로 실행됩니다."
                }
            ],
            "Chapter5 - 배열": [
                {
                    "question": "Java에서 배열의 인덱스는 몇부터 시작하나요?",
                    "options": [
                        "A) 0",
                        "B) 1", 
                        "C) -1",
                        "D) 사용자가 지정"
                    ],
                    "answer": "A) 0",
                    "explanation": "Java 배열의 인덱스는 0부터 시작합니다."
                },
                {
                    "question": "다음 중 2차원 배열 선언이 올바른 것은?",
                    "options": [
                        "A) int[][] arr = new int[3][];",
                        "B) int arr[][] = new int[][3];", 
                        "C) int[] arr[] = new int[3];",
                        "D) int arr[3][3] = new int;"
                    ],
                    "answer": "A) int[][] arr = new int[3][];",
                    "explanation": "2차원 배열은 행의 개수만 지정하고 열의 개수는 나중에 지정할 수 있습니다."
                }
            ],
            "Chapter6 - 객체지향 프로그래밍 I": [
                {
                    "question": "Java에서 클래스와 객체의 관계는?",
                    "options": [
                        "A) 클래스는 객체의 설계도",
                        "B) 객체는 클래스의 설계도", 
                        "C) 클래스와 객체는 동일한 개념",
                        "D) 관계가 없음"
                    ],
                    "answer": "A) 클래스는 객체의 설계도",
                    "explanation": "클래스는 객체를 생성하기 위한 설계도이고, 객체는 클래스의 인스턴스입니다."
                },
                {
                    "question": "다음 중 생성자의 특징이 아닌 것은?",
                    "options": [
                        "A) 클래스명과 동일한 이름",
                        "B) 반환값이 없음", 
                        "C) 객체 생성 시 자동 호출",
                        "D) static 키워드 사용"
                    ],
                    "answer": "D) static 키워드 사용",
                    "explanation": "생성자는 static 키워드를 사용하지 않습니다. static은 클래스 멤버에 사용됩니다."
                }
            ]
        }
    
    def _load_keywords(self) -> List[Dict[str, Any]]:
        """키워드 파일을 로드합니다."""
        try:
            keywords_file = "keywords.json"
            if os.path.exists(keywords_file):
                with open(keywords_file, 'r', encoding='utf-8') as f:
                    keywords = json.load(f)
                print(f"📂 키워드 로드: {len(keywords)}개 키워드")
                return keywords
            else:
                print("⚠️ keywords.json 파일을 찾을 수 없습니다.")
                return []
        except Exception as e:
            print(f"⚠️ 키워드 로딩 오류: {e}")
            return []
    
    def setup_documents(self, chunks: List[Document]) -> bool:
        """문서를 설정합니다."""
        try:
            self.documents = chunks
            print(f"✅ 문서 설정 완료: {len(chunks)}개 청크")
            return True
        except Exception as e:
            print(f"❌ 문서 설정 실패: {e}")
            return False
    
    def generate_question_with_rag(self, query: str, difficulty: str = "보통", question_type: str = "객관식") -> Dict[str, Any]:
        """
        향상된 로컬 임베딩을 사용하여 문제를 생성합니다.
        
        Args:
            query: 문제 생성 쿼리
            difficulty: 문제 난이도
            question_type: 문제 유형
            
        Returns:
            생성된 문제 정보
        """
        if not self.documents:
            return {
                "success": False,
                "message": "문서가 설정되지 않았습니다."
            }
        
        try:
            # 쿼리 분석 및 챕터 매핑
            chapter = self._map_query_to_chapter(query)
            
            # 로컬 임베딩을 사용한 유사도 검색
            relevant_docs = self.local_pdf_service.similarity_search(query, self.documents, k=3)
            
            if not relevant_docs:
                return {
                    "success": False,
                    "message": "관련 컨텍스트를 찾을 수 없습니다."
                }
            
            # 챕터별 문제 템플릿 선택
            question_template = self._select_chapter_question_template(chapter, query)
            
            if question_template:
                # 문제 텍스트에서 정답 정보 제거
                question_text = question_template["question"]
                import re
                question_text = re.sub(r'\[정답 정보:.*?\]', '', question_text, flags=re.DOTALL).strip()
                question_text = re.sub(r'정답 정보:.*?$', '', question_text, flags=re.DOTALL).strip()
                question_text = re.sub(r'\[정답.*?\]', '', question_text, flags=re.DOTALL).strip()
                question_text = re.sub(r'정답.*?$', '', question_text, flags=re.DOTALL).strip()
                
                return {
                    "success": True,
                    "message": "문제 생성이 완료되었습니다.",
                    "question": question_text,
                    "answer": question_template["answer"],
                    "explanation": question_template["explanation"],
                    "difficulty": difficulty,
                    "question_type": question_type,
                    "context_used": len(relevant_docs),
                    "options": question_template.get("options", []),
                    "chapter": chapter,
                    "concept_keywords": self._extract_keywords_from_query(query)
                }
            else:
                # 기본 문제 생성
                return self._generate_basic_question(query, relevant_docs, difficulty, question_type, chapter)
            
        except Exception as e:
            return {
                "success": False,
                "message": f"문제 생성 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _map_query_to_chapter(self, query: str) -> str:
        """쿼리를 챕터로 매핑합니다."""
        query_lower = query.lower()
        
        # 키워드 기반 매핑
        keyword_mapping = {
            "변수": "Chapter2 - 변수",
            "매개변수": "Chapter6 - 객체지향 프로그래밍 I",
            "parameter": "Chapter6 - 객체지향 프로그래밍 I",
            "연산자": "Chapter3 - 연산자",
            "조건문": "Chapter4 - 조건문과 반복문",
            "반복문": "Chapter4 - 조건문과 반복문",
            "for": "Chapter4 - 조건문과 반복문",
            "if": "Chapter4 - 조건문과 반복문",
            "while": "Chapter4 - 조건문과 반복문",
            "배열": "Chapter5 - 배열",
            "객체": "Chapter6 - 객체지향 프로그래밍 I",
            "클래스": "Chapter6 - 객체지향 프로그래밍 I",
            "상속": "Chapter6 - 객체지향 프로그래밍 I",
            "쓰레드": "Chapter4 - 조건문과 반복문"
        }
        
        for keyword, chapter in keyword_mapping.items():
            if keyword in query_lower:
                return chapter
        
        # 정확한 챕터명인 경우
        for chapter_name in self.chapter_pages.keys():
            if chapter_name.lower() in query_lower or query_lower in chapter_name.lower():
                return chapter_name
        
        # 기본값
        return "Chapter2 - 변수"
    
    def _select_chapter_question_template(self, chapter: str, query: str) -> Optional[Dict]:
        """챕터에 따라 적절한 문제 템플릿을 선택합니다."""
        if chapter in self.chapter_question_templates:
            templates = self.chapter_question_templates[chapter]
            return random.choice(templates)
        return None
    
    def _extract_keywords_from_query(self, query: str) -> List[str]:
        """쿼리에서 키워드를 추출합니다."""
        keywords = []
        query_lower = query.lower()
        
        for keyword_data in self.keywords_data:
            word = keyword_data['word'].lower()
            if word in query_lower or query_lower in word:
                keywords.append(keyword_data['word'])
        
        return keywords[:5]  # 최대 5개 키워드
    
    def _generate_basic_question(self, query: str, relevant_docs: List[Document], difficulty: str, question_type: str, chapter: str) -> Dict[str, Any]:
        """기본 문제를 생성합니다."""
        # 관련 문서에서 키워드 추출
        context = "\n".join([doc.page_content for doc in relevant_docs])
        
        # 간단한 문제 생성
        question = f"다음 Java 관련 내용에 대한 문제입니다: {query}"
        answer = "정답은 관련 문서를 참고하여 확인하세요."
        explanation = f"이 문제는 {query}와 관련된 내용을 바탕으로 출제되었습니다."
        
        return {
            "success": True,
            "message": "기본 문제가 생성되었습니다.",
            "question": question,
            "answer": answer,
            "explanation": explanation,
            "difficulty": difficulty,
            "question_type": question_type,
            "context_used": len(relevant_docs),
            "chapter": chapter,
            "concept_keywords": self._extract_keywords_from_query(query)
        }
    
    def generate_multiple_questions(self, query: str, count: int, difficulty: str = "보통") -> List[str]:
        """
        여러 개의 문제를 생성합니다.
        """
        questions = []
        for i in range(count):
            result = self.generate_question_with_rag(query, difficulty, "객관식")
            if result["success"]:
                question_text = f"문제 {i+1}: {result['question']}\n정답: {result['answer']}\n해설: {result['explanation']}"
                questions.append(question_text)
        
        return questions
    
    def search_keywords(self, keyword: str) -> List[Dict[str, Any]]:
        """키워드로 페이지를 검색합니다."""
        try:
            if not self.keywords_data:
                return []
            
            # 동적 검색 로직
            search_results = self._dynamic_keyword_search(keyword)
            
            # 결과에 챕터 정보 추가
            for result in search_results:
                pages = result['pages']
                if pages:
                    result['chapter'] = self._get_chapter_by_page(pages[0])
            
            return search_results
                
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
        """단어 경계 검색"""
        boundary_matches = []
        for keyword_data in self.keywords_data:
            word = keyword_data['word'].lower().strip()
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
    
    def _get_chapter_by_page(self, page: int) -> str:
        """페이지 번호로 챕터를 찾습니다."""
        for chapter_name, (start, end) in self.chapter_pages.items():
            if start <= page <= end:
                return chapter_name
        return "알 수 없는 챕터"


# 싱글톤 인스턴스
_enhanced_local_question_generator_service = None

def get_enhanced_local_question_generator_service():
    global _enhanced_local_question_generator_service
    if _enhanced_local_question_generator_service is None:
        _enhanced_local_question_generator_service = EnhancedLocalQuestionGeneratorService()
    return _enhanced_local_question_generator_service 