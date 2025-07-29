"""
연습문제 생성 서비스
"""
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from langchain_community.vectorstores import ElasticsearchStore


class QuestionGeneratorService:
    """연습문제 생성 서비스"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            max_tokens=2000
        )
        self.vector_store = None
    
    def setup_vector_store(self, chunks: List[Document], index_name: str = "java_learning_docs"):
        """벡터 스토어를 설정합니다."""
        try:
            from langchain_openai import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings()
            
            # Elasticsearch 벡터 스토어 생성
            self.vector_store = ElasticsearchStore.from_documents(
                documents=chunks,
                embedding=embeddings,
                es_url="http://localhost:9200",
                index_name=index_name
            )
            
            print(f"✅ Elasticsearch 벡터 스토어 설정 완료: {index_name}")
            return True
            
        except Exception as e:
            print(f"❌ Elasticsearch 벡터 스토어 설정 실패: {e}")
            return False
    
    def generate_question(self, context: str, difficulty: str = "보통", question_type: str = "객관식") -> str:
        """
        주어진 컨텍스트를 바탕으로 연습문제를 생성합니다.
        
        Args:
            context: 문제 생성에 사용할 컨텍스트
            difficulty: 난이도 (쉬움, 보통, 어려움)
            question_type: 문제 유형 (객관식, 주관식, 코드작성)
            
        Returns:
            생성된 연습문제
        """
        prompt = f"""
다음 Java 교재 내용을 바탕으로 {difficulty} 난이도의 {question_type} 문제를 생성해주세요.

**컨텍스트:**
{context}

**요구사항:**
1. 난이도: {difficulty}
2. 문제 유형: {question_type}
3. Java 프로그래밍 관련 문제
4. 명확하고 이해하기 쉬운 문제
5. 정답과 함께 생성

**출력 형식:**
문제: [문제 내용]
정답: [정답]
해설: [해설]

문제를 생성해주세요.
"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            print(f"❌ 문제 생성 실패: {e}")
            return f"문제 생성 중 오류가 발생했습니다: {e}"
    
    def generate_question_with_rag(self, query: str, difficulty: str = "보통", question_type: str = "객관식", k: int = 3) -> str:
        """
        RAG를 사용하여 연습문제를 생성합니다.
        
        Args:
            query: 검색 쿼리
            difficulty: 난이도
            question_type: 문제 유형
            k: 검색할 문서 수
            
        Returns:
            생성된 연습문제
        """
        if not self.vector_store:
            return "❌ 벡터 스토어가 설정되지 않았습니다."
        
        try:
            # 유사도 검색으로 관련 문서 찾기
            docs = self.vector_store.similarity_search(query, k=k)
            
            # 관련 문서들을 하나의 컨텍스트로 결합
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # 문제 생성
            return self.generate_question(context, difficulty, question_type)
            
        except Exception as e:
            print(f"❌ RAG 문제 생성 실패: {e}")
            return f"RAG 문제 생성 중 오류가 발생했습니다: {e}"
    
    def generate_multiple_questions(self, query: str, count: int = 3, difficulty: str = "보통") -> List[str]:
        """
        여러 개의 연습문제를 생성합니다.
        
        Args:
            query: 검색 쿼리
            count: 생성할 문제 수
            difficulty: 난이도
            
        Returns:
            생성된 문제 리스트
        """
        questions = []
        question_types = ["객관식", "주관식", "코드작성"]
        
        for i in range(count):
            question_type = question_types[i % len(question_types)]
            question = self.generate_question_with_rag(query, difficulty, question_type)
            questions.append(question)
        
        return questions


# 싱글톤 인스턴스
question_generator_service = QuestionGeneratorService() 