#!/usr/bin/env python3
"""
채팅 API 엔드포인트 테스트 스크립트
"""
import requests
import json
import time
from typing import Dict, Any


class ChatAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_ping(self) -> bool:
        """ping 엔드포인트 테스트"""
        print("🔍 Testing /ping endpoint...")
        try:
            response = self.session.get(f"{self.base_url}/api/v1/ping")
            if response.status_code == 200:
                print("✅ Ping successful:", response.json())
                return True
            else:
                print("❌ Ping failed:", response.status_code, response.text)
                return False
        except Exception as e:
            print(f"❌ Ping error: {e}")
            return False
    
    def test_chat_endpoint(self, chat_state: str, content: str = "테스트 메시지") -> Dict[str, Any]:
        """채팅 엔드포인트 테스트"""
        print(f"🔍 Testing chat endpoint with state: {chat_state}")
        
        payload = {
            "userId": 123,
            "bookId": 456,
            "sender": "USER",
            "content": content,
            "messageType": "TEXT",
            "chatState": chat_state
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {chat_state} successful:")
                print(f"   Content: {result.get('content', '')[:100]}...")
                print(f"   ChatState: {result.get('chatState', '')}")
                return result
            else:
                print(f"❌ {chat_state} failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ {chat_state} error: {e}")
            return {"error": str(e)}
    
    def run_all_tests(self):
        """모든 API 엔드포인트 테스트 실행"""
        print("🚀 Starting Chat API Tests...")
        print("=" * 50)
        
        # 1. Ping 테스트
        if not self.test_ping():
            print("❌ Ping test failed. Server might not be running.")
            return
        
        print("\n" + "=" * 50)
        print("📝 Testing Chat Endpoints...")
        print("=" * 50)
        
        # 2. 각 채팅 상태별 테스트
        test_cases = [
            {
                "state": "GENERATING_QUESTION_WITH_RAG",
                "content": "Java 변수와 데이터 타입에 대한 문제를 만들어주세요"
            },
            {
                "state": "GENERATING_ADDITIONAL_QUESTION_WITH_RAG", 
                "content": "추가 문제를 만들어주세요"
            },
            {
                "state": "EVALUATING_ANSWER_AND_LOGGING",
                "content": "정답입니다"
            },
            {
                "state": "PRESENTING_CONCEPT_EXPLANATION",
                "content": "Java 클래스와 객체에 대해 설명해주세요"
            },
            {
                "state": "REEXPLAINING_CONCEPT",
                "content": "이해가 안 됩니다. 더 쉽게 설명해주세요"
            },
            {
                "state": "WAITING_KEYWORD_FOR_PAGE_SEARCH",
                "content": "변수"
            },
            {
                "state": "PROCESSING_PAGE_SEARCH_RESULT",
                "content": "Java 배열"
            }
        ]
        
        results = {}
        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['state']}")
            result = self.test_chat_endpoint(
                test_case['state'], 
                test_case['content']
            )
            results[test_case['state']] = result
            time.sleep(1)  # 요청 간 간격
        
        # 3. 결과 요약
        print("\n" + "=" * 50)
        print("📊 Test Results Summary")
        print("=" * 50)
        
        success_count = 0
        total_count = len(test_cases)
        
        for state, result in results.items():
            if "error" not in result:
                print(f"✅ {state}: SUCCESS")
                success_count += 1
            else:
                print(f"❌ {state}: FAILED - {result.get('error', 'Unknown error')}")
        
        print(f"\n�� Overall Results: {success_count}/{total_count} tests passed")
        
        if success_count == total_count:
            print("🎉 All tests passed!")
        else:
            print("⚠️  Some tests failed. Check the logs above.")
        
        return results


def main():
    """메인 함수"""
    print("�� Chat API Tester")
    print("=" * 50)
    
    # 서버 URL 설정 (필요에 따라 변경)
    base_url = "http://localhost:8000"
    
    tester = ChatAPITester(base_url)
    results = tester.run_all_tests()
    
    # 결과를 JSON 파일로 저장
    with open("chat_api_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n�� Test results saved to: chat_api_test_results.json")


if __name__ == "__main__":
    main() 