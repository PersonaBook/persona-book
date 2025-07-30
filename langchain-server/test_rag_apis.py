#!/usr/bin/env python3
"""
RAG API 테스트 스크립트
6개의 RAG API를 모두 테스트합니다.
"""
import requests
import json
import time
import base64
from typing import Dict, Any


class RAGAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # 테스트용 PDF 데이터 (실제로는 파일에서 읽어와야 함)
        self.test_pdf_base64 = self._get_test_pdf_base64()
    
    def _get_test_pdf_base64(self) -> str:
        """테스트용 PDF Base64 데이터를 반환합니다."""
        # 실제 테스트에서는 PDF 파일을 읽어와야 합니다
        # 여기서는 더미 데이터를 반환합니다
        return "dummy_pdf_base64_data_for_testing"
    
    def test_health_check(self) -> bool:
        """헬스 체크 테스트"""
        print("🔍 Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health check successful:", response.json())
                return True
            else:
                print("❌ Health check failed:", response.status_code, response.text)
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_generating_question_with_rag(self) -> Dict[str, Any]:
        """GENERATING_QUESTION_WITH_RAG API 테스트"""
        print("🔍 Testing GENERATING_QUESTION_WITH_RAG API...")
        
        payload = {
            "userId": 123,
            "bookId": 456,
            "pdf_base64": self.test_pdf_base64,
            "query": "Java 변수와 데이터 타입에 대한 문제를 만들어주세요",
            "difficulty": "보통",
            "question_type": "객관식",
            "max_pages": 5
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/generate-question-with-rag",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ GENERATING_QUESTION_WITH_RAG successful:")
                print(f"   Question: {result.get('question', '')[:100]}...")
                print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
                return result
            else:
                print(f"❌ GENERATING_QUESTION_WITH_RAG failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ GENERATING_QUESTION_WITH_RAG error: {e}")
            return {"error": str(e)}
    
    def test_generating_additional_question_with_rag(self) -> Dict[str, Any]:
        """GENERATING_ADDITIONAL_QUESTION_WITH_RAG API 테스트"""
        print("🔍 Testing GENERATING_ADDITIONAL_QUESTION_WITH_RAG API...")
        
        payload = {
            "userId": 123,
            "bookId": 456,
            "pdf_base64": self.test_pdf_base64,
            "query": "추가 문제를 만들어주세요",
            "previous_question_type": "객관식",
            "difficulty": "보통",
            "max_pages": 5
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/generate-additional-question-with-rag",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ GENERATING_ADDITIONAL_QUESTION_WITH_RAG successful:")
                print(f"   Additional Question: {result.get('additional_question', '')[:100]}...")
                print(f"   Processing time: {result.get('processing_time', 0):.2f}s")
                return result
            else:
                print(f"❌ GENERATING_ADDITIONAL_QUESTION_WITH_RAG failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ GENERATING_ADDITIONAL_QUESTION_WITH_RAG error: {e}")
            return {"error": str(e)}
    
    def test_evaluating_answer_and_logging(self) -> Dict[str, Any]:
        """EVALUATING_ANSWER_AND_LOGGING API 테스트"""
        print("🔍 Testing EVALUATING_ANSWER_AND_LOGGING API...")
        
        payload = {
            "userId": 123,
            "bookId": 456,
            "question": "Java에서 변수의 선언 방법은?",
            "user_answer": "int number = 10;",
            "correct_answer": "int number = 10;",
            "explanation": "변수는 데이터 타입과 함께 선언하고 초기화할 수 있습니다.",
            "evaluation": "정답"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/evaluate-answer-and-log",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ EVALUATING_ANSWER_AND_LOGGING successful:")
                print(f"   Is Correct: {result.get('is_correct', False)}")
                print(f"   Score: {result.get('score', 0)}")
                return result
            else:
                print(f"❌ EVALUATING_ANSWER_AND_LOGGING failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ EVALUATING_ANSWER_AND_LOGGING error: {e}")
            return {"error": str(e)}
    
    def test_presenting_concept_explanation(self) -> Dict[str, Any]:
        """PRESENTING_CONCEPT_EXPLANATION API 테스트"""
        print("🔍 Testing PRESENTING_CONCEPT_EXPLANATION API...")
        
        payload = {
            "userId": 123,
            "bookId": 456,
            "pdf_base64": self.test_pdf_base64,
            "concept_query": "Java 클래스와 객체에 대해 설명해주세요",
            "user_level": "초급",
            "max_pages": 5
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/present-concept-explanation",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ PRESENTING_CONCEPT_EXPLANATION successful:")
                print(f"   Concept: {result.get('concept_name', '')}")
                print(f"   Explanation: {result.get('explanation', '')[:100]}...")
                return result
            else:
                print(f"❌ PRESENTING_CONCEPT_EXPLANATION failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ PRESENTING_CONCEPT_EXPLANATION error: {e}")
            return {"error": str(e)}
    
    def test_reexplaining_concept(self) -> Dict[str, Any]:
        """REEXPLAINING_CONCEPT API 테스트"""
        print("🔍 Testing REEXPLAINING_CONCEPT API...")
        
        payload = {
            "userId": 123,
            "bookId": 456,
            "pdf_base64": self.test_pdf_base64,
            "original_concept": "Java 클래스와 객체",
            "user_feedback": "이해가 안 됩니다. 더 쉽게 설명해주세요",
            "difficulty_level": "더 쉬운",
            "max_pages": 5
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/reexplain-concept",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ REEXPLAINING_CONCEPT successful:")
                print(f"   Concept: {result.get('concept_name', '')}")
                print(f"   Reexplanation: {result.get('reexplanation', '')[:100]}...")
                return result
            else:
                print(f"❌ REEXPLAINING_CONCEPT failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ REEXPLAINING_CONCEPT error: {e}")
            return {"error": str(e)}
    
    def test_processing_page_search_result(self) -> Dict[str, Any]:
        """PROCESSING_PAGE_SEARCH_RESULT API 테스트"""
        print("🔍 Testing PROCESSING_PAGE_SEARCH_RESULT API...")
        
        payload = {
            "userId": 123,
            "bookId": 456,
            "pdf_base64": self.test_pdf_base64,
            "search_keyword": "Java 배열",
            "search_type": "concept",
            "max_results": 5,
            "max_pages": 5
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/process-page-search-result",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ PROCESSING_PAGE_SEARCH_RESULT successful:")
                print(f"   Search Keyword: {result.get('search_keyword', '')}")
                print(f"   Total Results: {result.get('total_results', 0)}")
                return result
            else:
                print(f"❌ PROCESSING_PAGE_SEARCH_RESULT failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ PROCESSING_PAGE_SEARCH_RESULT error: {e}")
            return {"error": str(e)}
    
    def run_all_tests(self):
        """모든 RAG API 테스트 실행"""
        print("🚀 Starting RAG API Tests...")
        print("=" * 60)
        
        # 1. 헬스 체크
        if not self.test_health_check():
            print("❌ Health check failed. Server might not be running.")
            return
        
        print("\n" + "=" * 60)
        print("📝 Testing RAG APIs...")
        print("=" * 60)
        
        # 2. 각 API 테스트
        test_cases = [
            ("GENERATING_QUESTION_WITH_RAG", self.test_generating_question_with_rag),
            ("GENERATING_ADDITIONAL_QUESTION_WITH_RAG", self.test_generating_additional_question_with_rag),
            ("EVALUATING_ANSWER_AND_LOGGING", self.test_evaluating_answer_and_logging),
            ("PRESENTING_CONCEPT_EXPLANATION", self.test_presenting_concept_explanation),
            ("REEXPLAINING_CONCEPT", self.test_reexplaining_concept),
            ("PROCESSING_PAGE_SEARCH_RESULT", self.test_processing_page_search_result)
        ]
        
        results = {}
        for test_name, test_func in test_cases:
            print(f"\n🧪 Testing: {test_name}")
            result = test_func()
            results[test_name] = result
            time.sleep(1)  # 요청 간 간격
        
        # 3. 결과 요약
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        
        success_count = 0
        total_count = len(test_cases)
        
        for test_name, result in results.items():
            if "error" not in result:
                print(f"✅ {test_name}: SUCCESS")
                success_count += 1
            else:
                print(f"❌ {test_name}: FAILED - {result.get('error', 'Unknown error')}")
        
        print(f"\n🎯 Overall Results: {success_count}/{total_count} tests passed")
        
        if success_count == total_count:
            print("🎉 All RAG API tests passed!")
        else:
            print("⚠️  Some tests failed. Check the logs above.")
        
        return results


def main():
    """메인 함수"""
    print("🤖 RAG API Tester")
    print("=" * 60)
    
    # 서버 URL 설정 (필요에 따라 변경)
    base_url = "http://localhost:8000"
    
    tester = RAGAPITester(base_url)
    results = tester.run_all_tests()
    
    # 결과를 JSON 파일로 저장
    with open("rag_api_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Test results saved to: rag_api_test_results.json")


if __name__ == "__main__":
    main() 