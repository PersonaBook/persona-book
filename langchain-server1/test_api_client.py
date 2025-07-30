"""
FastAPI 서버 테스트 클라이언트
Java Learning System API를 테스트하는 스크립트
"""

import requests
import json
from typing import Dict, Any

class APITestClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health(self):
        """서버 상태 확인"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            print(f"✅ Health Check: {response.status_code}")
            print(f"Response: {response.json()}")
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Health Check 실패: {e}")
            return False
    
    def test_generate_question(self):
        """문제 생성 테스트"""
        try:
            payload = {
                "context": "Java에서 변수는 데이터를 저장하는 메모리 공간입니다.",
                "difficulty": "보통",
                "topic": "변수",
                "question_type": "개념이해"
            }
            
            response = self.session.post(f"{self.base_url}/generate_question", json=payload)
            print(f"✅ 문제 생성: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"생성된 문제: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return result
            else:
                print(f"❌ 문제 생성 실패: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 문제 생성 테스트 실패: {e}")
            return None
    
    def test_evaluate_answer(self, question: Dict[str, Any]):
        """답변 평가 테스트"""
        try:
            payload = {
                "question": question,
                "user_answer": 1,
                "is_correct": True,
                "concept_keywords": ["변수", "데이터타입"]
            }
            
            response = self.session.post(f"{self.base_url}/evaluate_answer", json=payload)
            print(f"✅ 답변 평가: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"평가 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return result
            else:
                print(f"❌ 답변 평가 실패: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 답변 평가 테스트 실패: {e}")
            return None
    
    def test_explain_concept(self):
        """개념 설명 테스트"""
        try:
            payload = {
                "concept_keyword": "변수",
                "wrong_answer_context": "사용자가 변수 개념을 잘못 이해함"
            }
            
            response = self.session.post(f"{self.base_url}/explain_concept", json=payload)
            print(f"✅ 개념 설명: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"개념 설명: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return result
            else:
                print(f"❌ 개념 설명 실패: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 개념 설명 테스트 실패: {e}")
            return None
    
    def test_search_pages(self):
        """페이지 검색 테스트"""
        try:
            payload = {
                "keyword": "변수"
            }
            
            response = self.session.post(f"{self.base_url}/search_pages", json=payload)
            print(f"✅ 페이지 검색: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"검색 결과: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return result
            else:
                print(f"❌ 페이지 검색 실패: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 페이지 검색 테스트 실패: {e}")
            return None
    
    def test_get_keywords(self):
        """키워드 목록 조회 테스트"""
        try:
            response = self.session.get(f"{self.base_url}/keywords")
            print(f"✅ 키워드 조회: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"키워드 목록: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return result
            else:
                print(f"❌ 키워드 조회 실패: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 키워드 조회 테스트 실패: {e}")
            return None
    
    def test_get_chapters(self):
        """챕터 정보 조회 테스트"""
        try:
            response = self.session.get(f"{self.base_url}/chapters")
            print(f"✅ 챕터 조회: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"챕터 정보: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return result
            else:
                print(f"❌ 챕터 조회 실패: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 챕터 조회 테스트 실패: {e}")
            return None
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 FastAPI 서버 테스트 시작")
        print("=" * 50)
        
        # 1. Health Check
        if not self.test_health():
            print("❌ 서버가 실행되지 않았습니다. 먼저 서버를 시작해주세요.")
            return
        
        print("\n" + "=" * 50)
        
        # 2. 키워드 조회
        self.test_get_keywords()
        
        print("\n" + "=" * 50)
        
        # 3. 챕터 정보 조회
        self.test_get_chapters()
        
        print("\n" + "=" * 50)
        
        # 4. 페이지 검색
        self.test_search_pages()
        
        print("\n" + "=" * 50)
        
        # 5. 문제 생성
        question_result = self.test_generate_question()
        
        print("\n" + "=" * 50)
        
        # 6. 답변 평가 (문제가 생성된 경우에만)
        if question_result and question_result.get('success'):
            self.test_evaluate_answer(question_result['question'])
        
        print("\n" + "=" * 50)
        
        # 7. 개념 설명
        self.test_explain_concept()
        
        print("\n" + "=" * 50)
        print("✅ 모든 테스트 완료!")

def main():
    """메인 함수"""
    client = APITestClient()
    client.run_all_tests()

if __name__ == "__main__":
    main() 