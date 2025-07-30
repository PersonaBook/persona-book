"""
개념 설명 시스템
"""

from typing import Optional

class ConceptExplainer:
    """개념 설명 시스템"""
    
    def __init__(self, chain_executor, vector_store_manager):
        self.chain_executor = chain_executor
        self.vector_store_manager = vector_store_manager
    
    def explain_concept(self, concept: str) -> Optional[str]:
        """개념에 대한 설명을 생성합니다."""
        try:
            retriever = self.vector_store_manager.get_retriever()
            if not retriever:
                return None
            
            # 관련 문서 검색
            docs = retriever.get_relevant_documents(concept)
            context = "\n".join([doc.page_content for doc in docs])
            
            # 설명 생성 프롬프트
            prompt = f"""
당신은 Java 교재 내용을 바탕으로 개념을 설명하는 AI입니다.
주어진 컨텍스트를 바탕으로 '{concept}'에 대한 명확하고 이해하기 쉬운 설명을 제공해주세요.

[컨텍스트]:
{context}

[개념]: {concept}

설명은 다음을 포함해야 합니다:
1. 개념의 정의
2. 사용 예시
3. 중요 포인트
4. 실제 활용 방법

설명:
"""
            
            # LLM으로 설명 생성
            response = self.chain_executor.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            print(f"❌ 개념 설명 생성 실패: {e}")
            return None
    
    def reexplain_concept(self, concept: str, user_feedback: str) -> Optional[str]:
        """사용자 피드백을 바탕으로 개념을 재설명합니다."""
        try:
            retriever = self.vector_store_manager.get_retriever()
            if not retriever:
                return None
            
            # 관련 문서 검색
            docs = retriever.get_relevant_documents(concept)
            context = "\n".join([doc.page_content for doc in docs])
            
            # 재설명 생성 프롬프트
            prompt = f"""
당신은 Java 교재 내용을 바탕으로 개념을 설명하는 AI입니다.
사용자의 피드백을 바탕으로 '{concept}'에 대한 더 나은 설명을 제공해주세요.

[컨텍스트]:
{context}

[개념]: {concept}
[사용자 피드백]: {user_feedback}

사용자의 피드백을 반영하여 더 명확하고 이해하기 쉬운 설명을 제공해주세요.
"""
            
            # LLM으로 재설명 생성
            response = self.chain_executor.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            print(f"❌ 개념 재설명 생성 실패: {e}")
            return None 