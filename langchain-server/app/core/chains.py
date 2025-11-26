"""
LangChain 체인 파이프라인 관리
"""

from typing import List, Optional
from langchain.chains import RetrievalQA
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import Document


class ChainFactory:
    """LangChain 체인 생성 팩토리"""
    
    @staticmethod
    def create_complete_chain_system(llm, retriever):
        """
        기존 호환성을 위한 래퍼 함수
        실제 구현은 create_rag_chain 사용 권장
        """
        class ChainExecutor:
            def __init__(self, llm, retriever):
                self.llm = llm
                self.retriever = retriever
        return None, ChainExecutor(llm, retriever)
    
    @staticmethod
    def create_rag_chain(llm, retriever, prompt_template: Optional[str] = None):
        """
        RAG (Retrieval-Augmented Generation) 체인 생성
        
        Args:
            llm: 언어 모델 인스턴스
            retriever: 벡터 스토어 retriever
            prompt_template: 선택적 커스텀 프롬프트 템플릿
            
        Returns:
            설정된 RAG 체인
        """
        if prompt_template is None:
            prompt_template = """다음 컨텍스트를 사용하여 질문에 답하세요.
컨텍스트를 찾을 수 없으면 모른다고 답하세요. 추측하지 마세요.

컨텍스트: {context}

질문: {question}

답변:"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
    
    @staticmethod
    def create_question_generation_chain(llm, context_template: Optional[str] = None):
        """
        문제 생성을 위한 체인 생성
        
        Args:
            llm: 언어 모델 인스턴스
            context_template: 선택적 커스텀 컨텍스트 템플릿
            
        Returns:
            문제 생성 체인
        """
        if context_template is None:
            context_template = """다음 교재 내용을 바탕으로 {difficulty} 난이도의 {question_type} 문제를 생성하세요.

교재 내용:
{context}

요구사항:
- 명확하고 이해하기 쉬운 문제
- {difficulty} 난이도에 맞는 수준
- 정답과 상세한 해설 포함

문제:"""
        
        prompt = ChatPromptTemplate.from_template(context_template)
        
        chain = (
            prompt
            | llm
            | StrOutputParser()
        )
        
        return chain
    
    @staticmethod
    def create_concept_explanation_chain(llm):
        """
        개념 설명 생성 체인
        
        Args:
            llm: 언어 모델 인스턴스
            
        Returns:
            개념 설명 체인
        """
        template = """다음 개념에 대해 명확하고 이해하기 쉽게 설명하세요.

개념: {concept}
사용자 수준: {user_level}

참고 자료:
{context}

요구사항:
1. 개념의 정의를 명확히 설명
2. 실생활 또는 프로그래밍 예시 포함
3. 핵심 포인트 강조
4. {user_level} 수준에 맞는 용어 사용
5. 간결하고 이해하기 쉬운 설명

설명:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        chain = (
            prompt
            | llm
            | StrOutputParser()
        )
        
        return chain
    
    @staticmethod
    def create_document_processing_chain(llm, retriever):
        """
        문서 처리 및 검색 체인 (LCEL 패턴)
        
        Args:
            llm: 언어 모델 인스턴스
            retriever: 벡터 스토어 retriever
            
        Returns:
            문서 처리 체인
        """
        template = """다음 문서들을 기반으로 질문에 답하세요:

{context}

질문: {question}
답변:"""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join([doc.page_content for doc in docs])
        
        chain = (
            RunnableParallel(
                context=(lambda x: x["question"]) | retriever | format_docs,
                question=RunnablePassthrough()
            )
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return chain 