"""
챕터 번호를 구체적인 내용으로 매핑하는 유틸리티
- JSON 기반 키워드 시스템
- 페이지 범위 지원
- 향상된 매핑 알고리즘
"""
import json
import re
import os
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from app.core.logging_config import get_logger

logger = get_logger(__name__)

# 전역 키워드 데이터 캐시
_keywords_cache = None

def load_keywords_data() -> Dict:
    """키워드 데이터를 JSON 파일에서 로드"""
    global _keywords_cache
    if _keywords_cache is not None:
        return _keywords_cache
    
    keywords_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'keywords.json')
    try:
        with open(keywords_path, 'r', encoding='utf-8') as f:
            _keywords_cache = json.load(f)
            logger.info(f"키워드 데이터 로드 완료: {len(_keywords_cache['chapters'])}개 챕터")
            return _keywords_cache
    except FileNotFoundError:
        logger.warning(f"키워드 파일을 찾을 수 없음: {keywords_path}")
        return {"chapters": {}}
    except json.JSONDecodeError as e:
        logger.error(f"키워드 파일 파싱 오류: {e}")
        return {"chapters": {}}

def extract_chapter_info(user_input: str) -> Tuple[Optional[str], List[str]]:
    """사용자 입력에서 챕터 번호와 키워드 추출"""
    input_normalized = user_input.strip().lower()
    
    # 챕터 번호 추출
    chapter_patterns = [
        r'챕터\s*(\d+)',
        r'chapter\s*(\d+)',
        r'(\d+)장',
        r'(\d+)챕터',
        r'^(\d+)$'
    ]
    
    chapter_num = None
    for pattern in chapter_patterns:
        match = re.search(pattern, input_normalized)
        if match:
            chapter_num = match.group(1)
            break
    
    # 추가 키워드 추출 (챕터 번호 제외)
    additional_keywords = []
    if chapter_num:
        # 챕터 번호 관련 텍스트 제거 후 나머지 키워드 추출
        clean_input = re.sub(r'(챕터|chapter|장)\s*\d+|\d+\s*(챕터|chapter|장)', '', input_normalized)
        additional_keywords = [word.strip() for word in clean_input.split() if word.strip()]
    else:
        # 챕터 번호가 없으면 전체를 키워드로 처리
        additional_keywords = [word.strip() for word in input_normalized.split() if word.strip()]
    
    return chapter_num, additional_keywords

def find_best_chapter_match(keywords: List[str]) -> Optional[str]:
    """키워드를 기반으로 가장 적합한 챕터 찾기"""
    keywords_data = load_keywords_data()
    chapters = keywords_data.get('chapters', {})
    
    if not keywords:
        return None
    
    chapter_scores = {}
    
    for chapter_id, chapter_info in chapters.items():
        score = 0
        chapter_keywords = [kw.lower() for kw in chapter_info.get('keywords', [])]
        
        for user_keyword in keywords:
            # 정확한 매치
            if user_keyword in chapter_keywords:
                score += 3
            # 부분 매치
            elif any(user_keyword in ck or ck in user_keyword for ck in chapter_keywords):
                score += 1
        
        if score > 0:
            chapter_scores[chapter_id] = score
    
    if chapter_scores:
        best_chapter = max(chapter_scores, key=chapter_scores.get)
        logger.debug(f"키워드 매칭으로 챕터 {best_chapter} 선택됨 (점수: {chapter_scores[best_chapter]})")
        return best_chapter
    
    return None

def get_chapter_content(chapter_id: str) -> str:
    """챕터 ID로부터 검색용 컨텐츠 생성"""
    keywords_data = load_keywords_data()
    chapters = keywords_data.get('chapters', {})
    
    if chapter_id not in chapters:
        return ""
    
    chapter_info = chapters[chapter_id]
    title = chapter_info.get('title', '')
    keywords = chapter_info.get('keywords', [])
    
    # 제목과 키워드를 결합하여 검색 쿼리 생성
    content = f"{title} {' '.join(keywords)}"
    return content

def map_chapter_to_content(user_input: str) -> str:
    """
    사용자 입력을 분석하여 구체적인 검색 쿼리로 변환
    
    Args:
        user_input: 사용자 입력 (예: "3", "챕터 3", "4장", "배열" 등)
        
    Returns:
        구체적인 검색 쿼리 문자열
    """
    if not user_input or user_input.strip() == "":
        return "Java 프로그래밍"
    
    # 챕터 정보와 키워드 추출
    chapter_num, additional_keywords = extract_chapter_info(user_input)
    
    logger.debug(f"입력 분석: 챕터={chapter_num}, 키워드={additional_keywords}")
    
    target_chapter = None
    
    # 1. 명시적 챕터 번호가 있는 경우
    if chapter_num:
        keywords_data = load_keywords_data()
        if chapter_num in keywords_data.get('chapters', {}):
            target_chapter = chapter_num
            logger.info(f"명시적 챕터 {chapter_num} 매핑됨")
    
    # 2. 키워드 기반 매칭
    if not target_chapter and additional_keywords:
        target_chapter = find_best_chapter_match(additional_keywords)
    
    # 3. 전체 입력을 키워드로 매칭 시도
    if not target_chapter:
        all_keywords = [word.strip() for word in user_input.lower().split() if word.strip()]
        target_chapter = find_best_chapter_match(all_keywords)
    
    # 결과 생성
    if target_chapter:
        content = get_chapter_content(target_chapter)
        # 추가 키워드가 있으면 포함
        if additional_keywords:
            content += " " + " ".join(additional_keywords)
        logger.info(f"최종 매핑: 챕터 {target_chapter} -> {content[:100]}...")
        return content
    else:
        # 매핑 실패 시 원본 반환
        logger.warning(f"매핑 실패, 원본 사용: {user_input}")
        return user_input

def get_chapter_page_range(chapter_id: str) -> Optional[Tuple[int, int]]:
    """챕터의 페이지 범위 반환"""
    keywords_data = load_keywords_data()
    chapters = keywords_data.get('chapters', {})
    
    if chapter_id in chapters:
        page_range = chapters[chapter_id].get('page_range')
        if page_range and len(page_range) == 2:
            return tuple(page_range)
    
    return None

def get_all_chapters_info() -> Dict:
    """모든 챕터 정보 반환"""
    return load_keywords_data().get('chapters', {})

def get_chapter_definitions():
    """챕터 정의를 반환합니다."""
    return {
        "2": {"name": "변수", "start": 30, "end": 107},
        "3": {"name": "연산자", "start": 108, "end": 157},
        "4": {"name": "조건문과 반복문", "start": 158, "end": 205},
        "5": {"name": "배열", "start": 206, "end": 253},
        "6": {"name": "객체지향 프로그래밍 I", "start": 254, "end": 339}
    }

def load_keywords_for_chapter(chapter_num):
    """특정 챕터의 키워드들을 keywords_detailed.json에서 로드합니다."""
    try:
        keywords_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'keywords_detailed.json')
        if not Path(keywords_path).exists():
            logger.warning(f"키워드 파일을 찾을 수 없습니다: {keywords_path}")
            return []
        
        with open(keywords_path, 'r', encoding='utf-8') as f:
            all_keywords = json.load(f)
        
        # 챕터 정의 가져오기
        chapters = get_chapter_definitions()
        if chapter_num not in chapters:
            logger.warning(f"챕터 {chapter_num}는 정의되지 않았습니다.")
            return []
        
        chapter_info = chapters[chapter_num]
        start_page = chapter_info['start']
        end_page = chapter_info['end']
        
        # 해당 챕터 페이지 범위에 속하는 키워드들 필터링
        chapter_keywords = []
        for keyword_data in all_keywords:
            keyword = keyword_data['word']
            pages = keyword_data['pages']
            
            # 키워드의 페이지 중 하나라도 챕터 범위에 속하면 포함
            for page in pages:
                if start_page <= page <= end_page:
                    chapter_keywords.append(keyword)
                    break
        
        logger.debug(f"챕터 {chapter_num} ({chapter_info['name']}) 키워드 {len(chapter_keywords)}개 로드됨")
        return chapter_keywords
        
    except Exception as e:
        logger.error(f"키워드 로딩 중 오류 발생: {e}")
        return []

def get_enhanced_chapter_content(chapter_num: str) -> str:
    """향상된 챕터 컨텐츠 생성 - 정밀한 키워드 기반"""
    try:
        chapter_keywords = load_keywords_for_chapter(chapter_num)
        if not chapter_keywords:
            # fallback to basic content
            return get_chapter_content(chapter_num)
        
        # 챕터 정의에서 제목 가져오기
        chapters = get_chapter_definitions()
        chapter_title = chapters.get(chapter_num, {}).get('name', f'챕터 {chapter_num}')
        
        # 키워드들을 결합하여 검색 쿼리 생성
        keywords_text = ' '.join(chapter_keywords)
        content = f"{chapter_title} {keywords_text}"
        
        logger.debug(f"향상된 챕터 {chapter_num} 컨텐츠 생성: {len(chapter_keywords)}개 키워드 사용")
        return content
        
    except Exception as e:
        logger.error(f"향상된 컨텐츠 생성 실패: {e}")
        return get_chapter_content(chapter_num)  # fallback


def enhance_query_for_search(query: str) -> str:
    """
    검색 쿼리를 더 구체적으로 향상시킴
    
    Args:
        query: 기본 쿼리
        
    Returns:
        향상된 검색 쿼리
    """
    # 매핑된 쿼리에 Java 관련 키워드 추가
    enhanced_query = f"Java {query} 프로그래밍 예제 문제"
    logger.debug(f"향상된 쿼리: {enhanced_query}")
    return enhanced_query