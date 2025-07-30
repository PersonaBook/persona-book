"""
문제 생성기 (LLM + RAG)
"""

from typing import List, Dict, Any, Optional
import json

class QuestionGenerator:
    """문제 생성기"""
    
    def __init__(self, llm, retriever):
        self.llm = llm
        self.retriever = retriever
    
    def generate_question(self, topic: str, difficulty: str = "보통") -> Optional[Dict[str, Any]]:
        """주제와 난이도를 바탕으로 문제를 생성합니다."""
        try:
            # 관련 문서 검색
            docs = self.retriever.get_relevant_documents(topic)
            context = "\n".join([doc.page_content for doc in docs])
            
            # 문제 생성 프롬프트
            prompt = f"""
당신은 Java 교재 내용을 바탕으로 문제를 출제하는 AI입니다.
주어진 컨텍스트를 바탕으로 '{topic}'에 대한 객관식 문제를 생성해주세요.

[컨텍스트]:
{context}

[주제]: {topic}
[난이도]: {difficulty}

다음 JSON 형식으로 문제를 생성해주세요:
{{
    "question": "문제 내용",
    "options": ["보기1", "보기2", "보기3", "보기4"],
    "correct_answer": 1,
    "explanation": "정답 설명",
    "quality_score": 0.8,
    "chapter": "챕터명",
    "concept_keywords": ["키워드1", "키워드2"]
}}

주의사항:
1. 문제는 명확하고 이해하기 쉬워야 합니다
2. 보기는 모두 타당해야 하며, 정답이 명확해야 합니다
3. 설명은 학습에 도움이 되도록 상세해야 합니다
4. quality_score는 0.0~1.0 사이의 값입니다

JSON:
"""
            
            # LLM으로 문제 생성
            response = self.llm.invoke(prompt)
            response_text = response.content.strip()
            print("\n[일반 문제 LLM 응답 전체 출력]====================\n", response_text, "\n==============================\n")
            # JSON 파싱
            try:
                # JSON 부분만 추출
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    response_text = response_text[json_start:json_end].strip()
                
                question_data = json.loads(response_text)
                
                # 필수 필드 검증
                required_fields = ["question", "options", "correct_answer", "explanation"]
                for field in required_fields:
                    if field not in question_data:
                        print(f"❌ 필수 필드 누락: {field}")
                        return None
                
                # 기본값 설정
                if "quality_score" not in question_data:
                    question_data["quality_score"] = 0.7
                if "chapter" not in question_data:
                    question_data["chapter"] = self._extract_chapter_from_topic(topic)
                if "concept_keywords" not in question_data:
                    question_data["concept_keywords"] = [topic]
                
                return question_data
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 실패: {e}")
                print(f"응답: {response_text}")
                return None
                
        except Exception as e:
            print(f"❌ 문제 생성 실패: {e}")
            return None
    
    def _extract_chapter_from_topic(self, topic: str) -> str:
        """토픽에서 챕터를 추출합니다."""
        topic_lower = topic.lower()
        
        if "변수" in topic_lower:
            return "Chapter1 - 변수"
        elif "연산자" in topic_lower:
            return "Chapter2 - 연산자"
        elif "조건문" in topic_lower or "반복문" in topic_lower or "for" in topic_lower or "if" in topic_lower:
            return "Chapter3 - 조건문과 반복문"
        elif "배열" in topic_lower:
            return "Chapter4 - 배열"
        elif "객체" in topic_lower or "클래스" in topic_lower or "상속" in topic_lower:
            return "Chapter5 - 객체지향 프로그래밍 I"
        else:
            return "기타" 