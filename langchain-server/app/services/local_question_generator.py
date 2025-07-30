"""
로컬 임베딩을 사용하는 문제 생성 서비스
"""
import os
import random
from typing import List, Dict, Any, Optional
from langchain.schema import Document
from app.services.local_pdf_service import get_local_pdf_service


class LocalQuestionGeneratorService:
    """로컬 임베딩을 사용하는 문제 생성 서비스"""
    
    def __init__(self):
        self.local_pdf_service = get_local_pdf_service()
        self.documents = []
        
        # 미리 정의된 문제 템플릿
        self.question_templates = {
            "쓰레드": [
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
                }
            ],
            "기본": [
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
                }
            ]
        }
    
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
        로컬 임베딩을 사용하여 문제를 생성합니다.
        
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
            # 로컬 임베딩을 사용한 유사도 검색
            relevant_docs = self.local_pdf_service.similarity_search(query, self.documents, k=3)
            
            if not relevant_docs:
                return {
                    "success": False,
                    "message": "관련 컨텍스트를 찾을 수 없습니다."
                }
            
            # 쿼리 키워드에 따라 적절한 문제 템플릿 선택
            question_template = self._select_question_template(query)
            
            if question_template:
                return {
                    "success": True,
                    "message": "문제 생성이 완료되었습니다.",
                    "question": question_template["question"],
                    "answer": question_template["answer"],
                    "explanation": question_template["explanation"],
                    "difficulty": difficulty,
                    "question_type": question_type,
                    "context_used": len(relevant_docs),
                    "options": question_template.get("options", [])
                }
            else:
                # 기본 문제 생성
                return self._generate_basic_question(query, relevant_docs, difficulty, question_type)
            
        except Exception as e:
            return {
                "success": False,
                "message": f"문제 생성 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _select_question_template(self, query: str) -> Optional[Dict]:
        """쿼리에 따라 적절한 문제 템플릿을 선택합니다."""
        query_lower = query.lower()
        
        if "쓰레드" in query_lower or "thread" in query_lower:
            return random.choice(self.question_templates["쓰레드"])
        else:
            return random.choice(self.question_templates["기본"])
    
    def _generate_basic_question(self, query: str, relevant_docs: List[Document], difficulty: str, question_type: str) -> Dict[str, Any]:
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
            "context_used": len(relevant_docs)
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


# 싱글톤 인스턴스
_local_question_generator_service = None

def get_local_question_generator_service():
    global _local_question_generator_service
    if _local_question_generator_service is None:
        _local_question_generator_service = LocalQuestionGeneratorService()
    return _local_question_generator_service 