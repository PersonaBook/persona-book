"""
적응형 학습 분석기
"""

from typing import List, Dict, Any

class WeaknessAnalyzer:
    """사용자 약점 분석기"""
    
    def __init__(self, chain_executor=None):
        self.chain_executor = chain_executor
    
    def analyze_user_weaknesses(self) -> Dict[str, Any]:
        """사용자의 약점을 분석합니다."""
        # 실제 구현에서는 사용자의 답변 기록을 분석
        return {
            "weak_concepts": ["변수", "배열"],
            "strong_concepts": ["연산자"],
            "overall_accuracy": 0.75,
            "recommendations": ["변수 개념을 더 학습하세요", "배열 활용법을 연습하세요"]
        }
    
    def get_weakness_keywords(self, limit: int = 5) -> List[str]:
        """약점 키워드를 반환합니다."""
        return ["변수", "배열", "for문", "if문", "클래스"]

class QuestionQualityAnalyzer:
    """문제 품질 평가 분석기"""
    
    def __init__(self, chain_executor=None):
        self.chain_executor = chain_executor
    
    def evaluate_question_quality(self, question: Dict[str, Any]) -> float:
        """문제의 품질을 평가합니다."""
        score = 0.0
        
        # 문제 명확성 평가
        if question.get("question"):
            score += 0.3
        
        # 보기 개수 평가
        options = question.get("options", [])
        if len(options) == 4:
            score += 0.2
        
        # 설명 존재 여부 평가
        if question.get("explanation"):
            score += 0.3
        
        # 품질 점수 평가
        quality_score = question.get("quality_score", 0.0)
        score += quality_score * 0.2
        
        return min(score, 1.0) 