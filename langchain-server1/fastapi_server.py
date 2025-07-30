"""
FastAPI 서버 - Java Learning System API
main.py의 기능들을 REST API로 제공
"""

import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

# FastAPI 관련 임포트
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 환경변수 로드
from dotenv import load_dotenv
load_dotenv()

# LangChain 관련 임포트
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

# 내부 모듈 임포트
from core.state_machine import ChatState, StateMachine
from core.models import ModelManager
from core.vector_store import VectorStoreManager
from core.chains import ChainFactory
from core.concept_explainer import ConceptExplainer
from utils.file_manager import ConfigManager, KeywordManager, AnswerHistoryManager
from generators.question_generator import QuestionGenerator
from analyzers.adaptive_learning import WeaknessAnalyzer, QuestionQualityAnalyzer

# Pydantic 모델들
class QuestionRequest(BaseModel):
    context: str
    difficulty: str = "보통"
    topic: str = "일반"
    question_type: str = "개념이해"

class AnswerEvaluationRequest(BaseModel):
    question: Dict[str, Any]
    user_answer: int
    is_correct: bool
    concept_keywords: List[str]

class ConceptExplanationRequest(BaseModel):
    concept_keyword: str
    wrong_answer_context: Optional[str] = None

class ConceptReexplanationRequest(BaseModel):
    concept_keyword: str
    user_feedback: str

class PageSearchRequest(BaseModel):
    keyword: str

# FastAPI 앱 생성
app = FastAPI(
    title="Java Learning System API",
    description="Java 학습을 위한 AI 기반 문제 생성 및 평가 시스템",
    version="1.0.0"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 전역 변수로 시스템 인스턴스 저장
java_system = None

def initialize_java_system():
    """Java 학습 시스템을 초기화합니다."""
    global java_system
    
    if java_system is None:
        from main import JavaLearningSystem
        java_system = JavaLearningSystem()
        success = java_system.initialize_system()
        if not success:
            raise HTTPException(status_code=500, detail="시스템 초기화 실패")
    
    return java_system

@app.on_event("startup")
async def startup_event():
    """서버 시작 시 시스템 초기화"""
    try:
        initialize_java_system()
        print("✅ Java Learning System 초기화 완료")
    except Exception as e:
        print(f"❌ 시스템 초기화 실패: {e}")

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "healthy", "message": "Java Learning System API is running"}

@app.post("/generate_question")
async def generate_question(request: QuestionRequest):
    """RAG 기반 문제 생성"""
    try:
        system = initialize_java_system()
        
        # 문제 생성
        question = system.question_generator.generate_question_with_rag(
            context=request.context,
            difficulty=request.difficulty,
            topic=request.topic,
            question_type=request.question_type
        )
        
        if question:
            return {
                "success": True,
                "question": question,
                "message": "문제가 성공적으로 생성되었습니다."
            }
        else:
            raise HTTPException(status_code=500, detail="문제 생성 실패")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문제 생성 중 오류: {str(e)}")

@app.post("/evaluate_answer")
async def evaluate_answer(request: AnswerEvaluationRequest):
    """답변 평가 및 로깅"""
    try:
        system = initialize_java_system()
        
        # 답변 평가
        evaluation_result = system.weakness_analyzer.evaluate_answer_and_log(
            question=request.question,
            user_answer=request.user_answer,
            is_correct=request.is_correct,
            concept_keywords=request.concept_keywords
        )
        
        return {
            "success": True,
            "evaluation": evaluation_result,
            "message": "답변이 평가되었습니다."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"답변 평가 중 오류: {str(e)}")

@app.post("/explain_concept")
async def explain_concept(request: ConceptExplanationRequest):
    """개념 설명 제공"""
    try:
        system = initialize_java_system()
        
        explanation = system.concept_explainer.present_concept_explanation(
            concept_keyword=request.concept_keyword,
            wrong_answer_context=request.wrong_answer_context
        )
        
        if explanation:
            return {
                "success": True,
                "explanation": explanation,
                "message": "개념 설명이 제공되었습니다."
            }
        else:
            raise HTTPException(status_code=404, detail="개념 설명을 찾을 수 없습니다.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"개념 설명 중 오류: {str(e)}")

@app.post("/reexplain_concept")
async def reexplain_concept(request: ConceptReexplanationRequest):
    """개념 재설명 제공"""
    try:
        system = initialize_java_system()
        
        reexplanation = system.concept_explainer.reexplain_concept(
            concept_keyword=request.concept_keyword,
            user_feedback=request.user_feedback
        )
        
        if reexplanation:
            return {
                "success": True,
                "reexplanation": reexplanation,
                "message": "개념이 재설명되었습니다."
            }
        else:
            raise HTTPException(status_code=404, detail="개념 재설명을 찾을 수 없습니다.")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"개념 재설명 중 오류: {str(e)}")

@app.post("/search_pages")
async def search_pages(request: PageSearchRequest):
    """키워드로 페이지 검색"""
    try:
        system = initialize_java_system()
        
        search_results = system._search_pages_by_keyword(request.keyword)
        
        return {
            "success": True,
            "keyword": request.keyword,
            "results": search_results,
            "message": f"'{request.keyword}' 키워드로 검색된 페이지들입니다."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"페이지 검색 중 오류: {str(e)}")

@app.get("/keywords")
async def get_keywords():
    """사용 가능한 키워드 목록 반환"""
    try:
        system = initialize_java_system()
        
        return {
            "success": True,
            "keywords": [kw['word'] for kw in system.keywords_data[:50]],  # 상위 50개만
            "total_count": len(system.keywords_data),
            "message": "사용 가능한 키워드 목록입니다."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"키워드 목록 조회 중 오류: {str(e)}")

@app.get("/chapters")
async def get_chapters():
    """챕터 정보 반환"""
    try:
        system = initialize_java_system()
        
        chapters = []
        for chapter_name, (start, end) in system.chapter_pages.items():
            chapters.append({
                "name": chapter_name,
                "start_page": start,
                "end_page": end,
                "total_pages": end - start + 1
            })
        
        return {
            "success": True,
            "chapters": chapters,
            "message": "Java 교재 챕터 정보입니다."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"챕터 정보 조회 중 오류: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "fastapi_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 