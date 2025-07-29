#!/usr/bin/env python3
"""
빠른 연습문제 생성 테스트 스크립트
"""
import os
import sys
import time
from app.services.pdf_service import pdf_service
from app.services.question_generator_service import QuestionGeneratorService
from app.services.cache_service import cache_service


def test_fast_question_generation():
    """빠른 연습문제 생성 테스트"""
    print("🚀 빠른 연습문제 생성 테스트 시작...")
    
    # 환경 변수 확인 - .env.prod에서 가져옴
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY 환경 변수가 설정되지 않았습니다. .env.prod 파일을 확인하세요.")
        return
    
    start_time = time.time()
    
    try:
        # 1. PDF 처리 (캐싱 적용)
        pdf_path = "./javajungsuk4_sample.pdf"
        max_pages = 5  # 테스트용으로 적은 페이지
        
        print("📄 PDF 처리 중...")
        chunks = cache_service.get_cached_chunks(pdf_path, max_pages)
        
        if not chunks:
            print("🔄 캐시에 없어서 PDF 처리 시작...")
            chunks = pdf_service.process_pdf_and_create_chunks(pdf_path, max_pages=max_pages)
            
            if chunks:
                cache_service.cache_chunks(pdf_path, chunks, max_pages)
        
        if not chunks:
            print("❌ PDF 처리 실패")
            return
        
        print(f"✅ PDF 처리 완료: {len(chunks)}개 청크")
        
        # 2. 문제 생성
        print("🤖 문제 생성 중...")
        question_service = QuestionGeneratorService()
        success = question_service.setup_vector_store(chunks)
        
        if not success:
            print("❌ 벡터 스토어 설정 실패")
            return
        
        # 3. RAG 문제 생성
        query = "Java 변수와 데이터 타입"
        question = question_service.generate_question_with_rag(
            query=query,
            difficulty="보통",
            question_type="객관식"
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\n⏱️  총 소요 시간: {duration:.2f}초")
        print(f"📝 생성된 문제:")
        print("=" * 50)
        print(question)
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    test_fast_question_generation() 