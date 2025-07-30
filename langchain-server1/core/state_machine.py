"""
상태 머신 및 FastAPI 클라이언트
ChatState enum을 사용한 상태 관리와 FastAPI 서버와의 통신
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
from enum import Enum

class ChatState(Enum):
    """채팅 상태 열거형"""
    # 기본 상태들
    INITIAL = "INITIAL"
    WAITING_USER_SELECT_FEATURE = "WAITING_USER_SELECT_FEATURE"
    
    # 문제 생성 관련 상태들
    WAITING_PROBLEM_CRITERIA_SELECTION = "WAITING_PROBLEM_CRITERIA_SELECTION"
    WAITING_PROBLEM_CONTEXT_INPUT = "WAITING_PROBLEM_CONTEXT_INPUT"
    GENERATING_QUESTION_WITH_RAG = "GENERATING_QUESTION_WITH_RAG"
    GENERATING_ADDITIONAL_QUESTION_WITH_RAG = "GENERATING_ADDITIONAL_QUESTION_WITH_RAG"
    QUESTION_PRESENTED_TO_USER = "QUESTION_PRESENTED_TO_USER"
    
    # 답변 평가 관련 상태들
    WAITING_USER_ANSWER = "WAITING_USER_ANSWER"
    EVALUATING_ANSWER_AND_LOGGING = "EVALUATING_ANSWER_AND_LOGGING"
    FEEDBACK_CORRECT = "FEEDBACK_CORRECT"
    FEEDBACK_INCORRECT = "FEEDBACK_INCORRECT"
    
    # 개념 설명 관련 상태들
    WAITING_CONCEPT_INPUT = "WAITING_CONCEPT_INPUT"
    PRESENTING_CONCEPT_EXPLANATION = "PRESENTING_CONCEPT_EXPLANATION"
    WAITING_CONCEPT_RATING = "WAITING_CONCEPT_RATING"
    WAITING_REASON_FOR_LOW_RATING = "WAITING_REASON_FOR_LOW_RATING"
    REEXPLAINING_CONCEPT = "REEXPLAINING_CONCEPT"
    
    # 페이지 검색 관련 상태들
    WAITING_KEYWORD_FOR_PAGE_SEARCH = "WAITING_KEYWORD_FOR_PAGE_SEARCH"
    PROCESSING_PAGE_SEARCH_RESULT = "PROCESSING_PAGE_SEARCH_RESULT"
    DISPLAYING_RESULTS = "DISPLAYING_RESULTS"
    
    # 학습 후 액션 관련 상태들
    WAITING_NEXT_ACTION_AFTER_LEARNING = "WAITING_NEXT_ACTION_AFTER_LEARNING"
    WAITING_FEEDBACK_SELECTION_AFTER_ANSWER = "WAITING_FEEDBACK_SELECTION_AFTER_ANSWER"
    
    # 오류 상태들
    ERROR = "ERROR"
    SYSTEM_ERROR = "SYSTEM_ERROR"

class FastAPIClient:
    """FastAPI 서버와 통신하는 클라이언트"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_server_health(self) -> bool:
        """서버 상태를 확인합니다."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ 서버 연결 실패: {e}")
            return False
    
    def generate_question_with_rag(self, context: str, difficulty: str = "보통", topic: str = "일반", question_type: str = "개념이해") -> Optional[Dict[str, Any]]:
        """RAG 기반 문제를 생성합니다."""
        try:
            payload = {
                "context": context,
                "difficulty": difficulty,
                "topic": topic,
                "question_type": question_type
            }
            
            response = self.session.post(f"{self.base_url}/generate_question", json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 문제 생성 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 문제 생성 중 오류: {e}")
            return None
    
    def evaluate_answer_and_log(self, question: Dict[str, Any], user_answer: int, is_correct: bool, concept_keywords: List[str]) -> Optional[Dict[str, Any]]:
        """답변을 평가하고 로깅합니다."""
        try:
            payload = {
                "question": question,
                "user_answer": user_answer,
                "is_correct": is_correct,
                "concept_keywords": concept_keywords
            }
            
            response = self.session.post(f"{self.base_url}/evaluate_answer", json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 답변 평가 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 답변 평가 중 오류: {e}")
            return None
    
    def present_concept_explanation(self, concept_keyword: str, wrong_answer_context: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """개념 설명을 생성합니다."""
        try:
            payload = {
                "concept_keyword": concept_keyword,
                "wrong_answer_context": wrong_answer_context
            }
            
            response = self.session.post(f"{self.base_url}/explain_concept", json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 개념 설명 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 개념 설명 중 오류: {e}")
            return None
    
    def reexplain_concept(self, concept_keyword: str, user_feedback: str) -> Optional[Dict[str, Any]]:
        """개념을 재설명합니다."""
        try:
            payload = {
                "concept_keyword": concept_keyword,
                "user_feedback": user_feedback
            }
            
            response = self.session.post(f"{self.base_url}/reexplain_concept", json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 개념 재설명 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 개념 재설명 중 오류: {e}")
            return None
    
    def process_page_search_result(self, keyword: str) -> Optional[Dict[str, Any]]:
        """페이지 검색 결과를 처리합니다."""
        try:
            payload = {"keyword": keyword}
            
            response = self.session.post(f"{self.base_url}/search_pages", json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 페이지 검색 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 페이지 검색 중 오류: {e}")
            return None

class StateMachine:
    """상태 머신 클래스"""
    
    def __init__(self):
        self.current_state = ChatState.INITIAL
        self.context = {}
        self.chat_history = []
        self.fastapi_client = FastAPIClient()
    
    def transition_to(self, new_state: ChatState):
        """상태를 전환합니다."""
        print(f"📊 현재 상태: {self.current_state.value}")
        self.current_state = new_state
    
    def go_back(self):
        """이전 상태로 돌아갑니다."""
        if self.chat_history:
            previous_state = self.chat_history.pop()
            self.current_state = previous_state
            print(f"📊 이전 상태로 돌아감: {self.current_state.value}")
    
    def add_to_chat_history(self, state: ChatState):
        """채팅 히스토리에 상태를 추가합니다."""
        self.chat_history.append(state)
    
    def update_context(self, key: str, value: Any):
        """컨텍스트를 업데이트합니다."""
        self.context[key] = value
    
    def get_context(self, key: str, default=None):
        """컨텍스트를 가져옵니다."""
        return self.context.get(key, default)
    
    def clear_context(self):
        """컨텍스트를 초기화합니다."""
        self.context.clear()
    
    def get_current_state(self) -> ChatState:
        """현재 상태를 반환합니다."""
        return self.current_state
    
    def is_fastapi_call_state(self) -> bool:
        """FastAPI 호출이 필요한 상태인지 확인합니다."""
        fastapi_states = [
            ChatState.GENERATING_QUESTION_WITH_RAG,
            ChatState.GENERATING_ADDITIONAL_QUESTION_WITH_RAG,
            ChatState.EVALUATING_ANSWER_AND_LOGGING,
            ChatState.PRESENTING_CONCEPT_EXPLANATION,
            ChatState.REEXPLAINING_CONCEPT,
            ChatState.PROCESSING_PAGE_SEARCH_RESULT
        ]
        return self.current_state in fastapi_states 