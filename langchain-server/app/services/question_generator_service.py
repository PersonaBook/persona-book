"""
연습문제 생성 서비스
"""
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document
from langchain_community.vectorstores import ElasticsearchStore

# 환경 변수 로드
load_dotenv('../.env.prod')
load_dotenv('.env.prod')
load_dotenv('.env')


class QuestionGeneratorService:
    """연습문제 생성 서비스"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=2000
        )
        self.vector_store = None
    
    def setup_vector_store(self, chunks: List[Document], index_name: str = "java_learning_docs"):
        """벡터 스토어를 설정합니다."""
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            embeddings = GoogleGenerativeAIEmbeddings(
                model="text-embedding-004"
            )
            
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
    
    def generate_question_with_rag(self, query: str, difficulty: str = "보통", question_type: str = "객관식") -> Dict[str, Any]:
        """
        RAG를 사용하여 문제를 생성합니다.
        
        Args:
            query: 문제 생성 쿼리
            difficulty: 문제 난이도
            question_type: 문제 유형
            
        Returns:
            생성된 문제 정보
        """
        if not self.vector_store:
            return {
                "success": False,
                "message": "벡터 스토어가 설정되지 않았습니다."
            }
        
        try:
            # 관련 컨텍스트 검색
            relevant_docs = self.vector_store.similarity_search(query, k=5)
            
            if not relevant_docs:
                return {
                    "success": False,
                    "message": "관련 컨텍스트를 찾을 수 없습니다."
                }
            
            # 컨텍스트 결합
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # 문제 생성 프롬프트
            prompt = f"""
다음 Java 교재 내용을 바탕으로 {difficulty} 난이도의 {question_type} 문제를 생성해주세요.

**요청 내용:**
- 쿼리: {query}
- 난이도: {difficulty}
- 문제 유형: {question_type}

**교재 내용:**
{context}

**요구사항:**
1. Java 프로그래밍 관련 문제
2. 명확하고 이해하기 쉬운 문제
3. 정답과 함께 생성
4. 상세한 해설 포함
5. {difficulty} 난이도에 맞는 문제

**출력 형식:**
문제: [문제 내용]
정답: [정답]
해설: [상세한 해설]

위 형식으로 문제를 생성해주세요.
"""
            
            # LLM을 사용한 문제 생성
            response = self.llm.invoke(prompt)
            
            # 응답 파싱
            content = response.content
            question, correct_answer, explanation = self._parse_generated_content(content)
            
            return {
                "success": True,
                "message": "문제 생성이 완료되었습니다.",
                "question": question,
                "correct_answer": correct_answer,
                "explanation": explanation,
                "difficulty": difficulty,
                "question_type": question_type,
                "chunks_used": len(relevant_docs)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"문제 생성 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _parse_generated_content(self, content: str) -> tuple[str, str, str]:
        """
        생성된 내용을 파싱하여 문제, 정답, 해설을 추출합니다.
        
        Args:
            content: 생성된 내용
            
        Returns:
            (문제, 정답, 해설)
        """
        try:
            lines = content.split('\n')
            question = ""
            correct_answer = ""
            explanation = ""
            
            current_section = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("문제:"):
                    current_section = "question"
                    question = line.replace("문제:", "").strip()
                elif line.startswith("정답:"):
                    current_section = "answer"
                    correct_answer = line.replace("정답:", "").strip()
                elif line.startswith("해설:"):
                    current_section = "explanation"
                    explanation = line.replace("해설:", "").strip()
                else:
                    if current_section == "question":
                        question += " " + line
                    elif current_section == "answer":
                        correct_answer += " " + line
                    elif current_section == "explanation":
                        explanation += " " + line
            
            # 기본값 설정
            if not question:
                question = content[:500] + "..." if len(content) > 500 else content
            if not correct_answer:
                correct_answer = "정답을 확인해주세요."
            if not explanation:
                explanation = "해설을 확인해주세요."
                
            return question.strip(), correct_answer.strip(), explanation.strip()
            
        except Exception as e:
            print(f"응답 파싱 오류: {e}")
            return content[:500], "정답을 확인해주세요.", "해설을 확인해주세요."


# 싱글톤 인스턴스
question_generator_service = QuestionGeneratorService() 