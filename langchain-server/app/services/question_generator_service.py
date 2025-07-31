"""
연습문제 생성 서비스
"""
import os
import re
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document
from langchain_community.vectorstores import ElasticsearchStore

# 환경 변수 로드 - config.py에서 이미 로드되므로 제거


class QuestionGeneratorService:
    """연습문제 생성 서비스"""
    
    def __init__(self):
        from app.core.config import settings
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.7,
            max_tokens=2000,
            google_api_key=settings.gemini_api_key
        )
        self.vector_store = None
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=settings.gemini_api_key
        )
        self.index_name = "java_learning_docs"  # 고정된 인덱스 이름
    
    
    def has_vector_store(self) -> bool:
        """벡터 스토어가 이미 존재하는지 확인"""
        if self.vector_store is not None:
            return True
            
        # Elasticsearch 인덱스 존재 여부 확인
        try:
            from elasticsearch import Elasticsearch
            es = Elasticsearch(['http://elasticsearch:9200'])
            return es.indices.exists(index=self.index_name)
        except Exception as e:
            print(f"❌ 인덱스 존재 확인 중 오류: {e}")
            return False
    
    def connect_to_existing_vector_store(self):
        """기존 벡터 스토어에 연결"""
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            from app.core.config import settings
            
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=settings.gemini_api_key
            )
            
            self.vector_store = ElasticsearchStore(
                embedding=embeddings,
                es_url="http://elasticsearch:9200",
                index_name=self.index_name
            )
            print(f"✅ 기존 벡터 스토어 연결 완료: {self.index_name}")
            return True
        except Exception as e:
            print(f"❌ 기존 벡터 스토어 연결 실패: {e}")
            return False
    
    def setup_vector_store(self, chunks: List[Document], index_name: str = "java_learning_docs"):
        """벡터 스토어를 설정합니다."""
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            from app.core.config import settings
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=settings.gemini_api_key
            )
            
            # Elasticsearch 벡터 스토어 생성
            self.vector_store = ElasticsearchStore.from_documents(
                documents=chunks,
                embedding=embeddings,
                es_url="http://elasticsearch:9200",
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
            if question_type == "객관식":
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
3. 정확히 4개의 선택지만 포함
4. 정답과 함께 생성 (1~4번 중 하나)
5. 상세한 해설 포함
6. {difficulty} 난이도에 맞는 문제

**중요: 반드시 아래 형식을 정확히 따라주세요. 추가 텍스트나 다른 선택지는 포함하지 마세요.**

**출력 형식:**
문제: [문제 내용]
보기1: [첫 번째 선택지]
보기2: [두 번째 선택지]
보기3: [세 번째 선택지]
보기4: [네 번째 선택지]
정답: [정답 번호 (1~4)]
해설: [상세한 해설]

위 형식 외에는 어떤 추가 내용도 포함하지 마세요.
"""
            else:
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
            print(f"🔍 LLM 응답 원본: {content}")
            question, correct_answer, explanation, options = self._parse_generated_content(content)
            print(f"🔍 파싱된 문제: {question}")
            print(f"🔍 파싱된 선택지: {options}")
            print(f"🔍 파싱된 정답: {correct_answer}")
            print(f"🔍 파싱된 해설: {explanation}")
            
            return {
                "success": True,
                "message": "문제 생성이 완료되었습니다.",
                "question": question,
                "correct_answer": correct_answer,
                "explanation": explanation,
                "options": options,
                "difficulty": difficulty,
                "question_type": question_type,
                "chunks_used": len(relevant_docs)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"문제 생성 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _parse_generated_content(self, content: str) -> tuple[str, str, str, list]:
        """
        생성된 내용을 파싱하여 문제, 정답, 해설, 선택지를 추출합니다.
        
        Args:
            content: 생성된 내용
            
        Returns:
            (문제, 정답, 해설, 선택지)
        """
        try:
            print(f"🔍 파싱할 원본 내용: {content}")
            
            lines = content.split('\n')
            question = ""
            correct_answer = ""
            explanation = ""
            choices = []
            
            current_section = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                if line.startswith("문제:"):
                    current_section = "question"
                    question = line.replace("문제:", "").strip()
                elif line.startswith("보기1:"):
                    current_section = "choice1"
                    if len(choices) < 4:  # 최대 4개만 허용
                        choices.append(line.replace("보기1:", "").strip())
                elif line.startswith("보기2:"):
                    current_section = "choice2"
                    if len(choices) < 4:
                        choices.append(line.replace("보기2:", "").strip())
                elif line.startswith("보기3:"):
                    current_section = "choice3"
                    if len(choices) < 4:
                        choices.append(line.replace("보기3:", "").strip())
                elif line.startswith("보기4:"):
                    current_section = "choice4"
                    if len(choices) < 4:
                        choices.append(line.replace("보기4:", "").strip())
                elif line.startswith("정답:") or "정답:" in line:
                    current_section = "answer"
                    # "정답:" 이후의 모든 내용을 추출
                    if "정답:" in line:
                        correct_answer = line.split("정답:", 1)[1].strip()
                elif line.startswith("해설:") or "해설:" in line:
                    current_section = "explanation"
                    # "해설:" 이후의 모든 내용을 추출
                    if "해설:" in line:
                        explanation = line.split("해설:", 1)[1].strip()
                else:
                    # 숫자로 시작하는 선택지 (1. 2. 3. 4. 형태) 처리 방지
                    if re.match(r'^\d+\.\s', line) and len(choices) >= 4:
                        continue  # 이미 4개 선택지가 있으면 추가 숫자 선택지 무시
                    
                    if current_section == "question":
                        question += " " + line
                    elif current_section in ["choice1", "choice2", "choice3", "choice4"]:
                        if len(choices) > 0 and len(choices) <= 4:
                            choices[-1] += " " + line
                    elif current_section == "answer":
                        correct_answer += " " + line
                    elif current_section == "explanation":
                        explanation += " " + line
            
            # 선택지가 4개가 아니면 추가로 파싱 시도 (숫자 형태)
            if len(choices) != 4:
                print(f"⚠️ 선택지가 {len(choices)}개, 추가 파싱 시도")
                
                # 1. 2. 3. 4. 형태의 선택지 찾기
                choice_pattern = r'^(\d+)\.\s+(.+)$'
                found_choices = []
                
                for line in lines:
                    line = line.strip()
                    match = re.match(choice_pattern, line)
                    if match and len(found_choices) < 4:
                        choice_num = int(match.group(1))
                        choice_text = match.group(2)
                        if 1 <= choice_num <= 4:
                            found_choices.append(choice_text)
                
                if len(found_choices) == 4:
                    choices = found_choices
                    print(f"✅ 숫자 형태 선택지 4개 파싱 성공")
            
            # 선택지를 정확히 4개로 제한
            choices = choices[:4]  # 4개 초과시 잘라내기
            
            # 기본값 설정
            if not question:
                question = content[:500] + "..." if len(content) > 500 else content
            if not correct_answer:
                correct_answer = "정답을 확인해주세요."
            if not explanation:
                explanation = "해설을 확인해주세요."
            if len(choices) != 4:
                choices = ["선택지1", "선택지2", "선택지3", "선택지4"]
            
            print(f"🔍 최종 파싱 결과: 문제={len(question)}글자, 선택지={len(choices)}개, 정답={correct_answer}, 해설={len(explanation)}글자")
                
            return question.strip(), correct_answer.strip(), explanation.strip(), choices
            
        except Exception as e:
            print(f"❌ 응답 파싱 오류: {e}")
            return content[:500], "정답을 확인해주세요.", "해설을 확인해주세요.", ["선택지1", "선택지2", "선택지3", "선택지4"]

# 싱글톤 인스턴스
question_generator_service = QuestionGeneratorService() 