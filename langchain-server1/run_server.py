#!/usr/bin/env python3
"""
FastAPI 서버 실행 스크립트
Java Learning System API 서버를 시작합니다.
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """필요한 의존성 확인"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'requests',
        'python-dotenv',
        'langchain-openai',
        'langchain-community',
        'faiss-cpu',
        'pypdf'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ 누락된 패키지: {', '.join(missing_packages)}")
        print("다음 명령어로 설치해주세요:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ 모든 의존성 확인 완료")
    return True

def check_environment():
    """환경 설정 확인"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env 파일이 없습니다.")
        print("OpenAI API 키를 설정해주세요:")
        print("OPENAI_API_KEY=your_api_key_here")
        return False
    
    # .env 파일에서 API 키 확인
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("❌ OPENAI_API_KEY가 설정되지 않았습니다.")
            return False
        
        print("✅ 환경 설정 확인 완료")
        return True
        
    except Exception as e:
        print(f"❌ 환경 설정 확인 실패: {e}")
        return False

def check_pdf_file():
    """PDF 파일 확인"""
    pdf_files = list(Path('.').glob('*.pdf'))
    if not pdf_files:
        print("❌ PDF 파일이 없습니다.")
        print("Java 교재 PDF 파일을 현재 디렉토리에 넣어주세요.")
        return False
    
    print(f"✅ PDF 파일 발견: {pdf_files[0].name}")
    return True

def wait_for_server(url: str = "http://localhost:8000", timeout: int = 30):
    """서버가 시작될 때까지 대기"""
    print(f"🔄 서버 시작 대기 중... ({timeout}초)")
    
    for i in range(timeout):
        try:
            response = requests.get(f"{url}/health", timeout=1)
            if response.status_code == 200:
                print("✅ 서버가 성공적으로 시작되었습니다!")
                return True
        except:
            pass
        
        time.sleep(1)
        if (i + 1) % 5 == 0:
            print(f"   {i + 1}초 경과...")
    
    print("❌ 서버 시작 시간 초과")
    return False

def start_server():
    """서버 시작"""
    print("🚀 Java Learning System API 서버 시작")
    print("=" * 50)
    
    # 1. 의존성 확인
    if not check_dependencies():
        return False
    
    # 2. 환경 설정 확인
    if not check_environment():
        return False
    
    # 3. PDF 파일 확인
    if not check_pdf_file():
        return False
    
    print("\n" + "=" * 50)
    print("📋 서버 정보:")
    print("   - URL: http://localhost:8000")
    print("   - API 문서: http://localhost:8000/docs")
    print("   - 대안 문서: http://localhost:8000/redoc")
    print("   - 종료: Ctrl+C")
    print("=" * 50)
    
    try:
        # 서버 시작
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "fastapi_server:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 서버가 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 시작 실패: {e}")
        return False
    
    return True

def main():
    """메인 함수"""
    start_server()

if __name__ == "__main__":
    main() 