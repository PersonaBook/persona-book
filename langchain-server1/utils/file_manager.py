"""
파일 관리 클래스들
설정, 키워드, 답변 기록 등의 파일 관리
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

class ConfigManager:
    """설정 관리 클래스"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """설정을 로드합니다."""
        default_config = {
            "pdf_path": "",
            "default_difficulty": "보통",
            "questions_per_batch": 20,
            "vector_store_k": 5,
            "semantic_chunker_threshold": 95,
            "openai_api_key": "",
            "model_name": "gpt-4o",
            "embedding_model": "text-embedding-3-small",
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 설정 파일 로드 실패: {e}")
                return default_config
        return default_config
    
    def get(self, key: str, default=None):
        """설정값을 가져옵니다."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """설정값을 변경합니다."""
        self.config[key] = value
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 설정 저장 실패: {e}")
            return False

class KeywordManager:
    """키워드 관리 클래스"""
    
    def __init__(self, keywords_file: str = "keywords.json"):
        self.keywords_file = keywords_file
        self.keywords_data = self.load_keywords()
    
    def load_keywords(self) -> Dict[str, List[str]]:
        """키워드를 로드합니다."""
        try:
            if os.path.exists(self.keywords_file):
                with open(self.keywords_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                
                # 리스트 형태의 키워드 데이터를 딕셔너리로 변환
                if isinstance(raw_data, list):
                    keywords_dict = {}
                    for item in raw_data:
                        if isinstance(item, dict) and 'word' in item and 'pages' in item:
                            # 챕터별로 키워드 분류
                            chapter = self._get_chapter_by_page(item['pages'][0])
                            if chapter not in keywords_dict:
                                keywords_dict[chapter] = []
                            keywords_dict[chapter].append(item['word'])
                    
                    print(f"📂 키워드 로드 완료: {len(keywords_dict)}개 챕터, {sum(len(v) for v in keywords_dict.values())}개 키워드")
                    return keywords_dict
                else:
                    print("📂 키워드 파일 형식이 예상과 다릅니다.")
                    return {}
            else:
                print("📂 키워드 파일이 없습니다.")
                return {}
                
        except Exception as e:
            print(f"⚠️ 키워드 로드 실패: {e}")
            return {}
    
    def _get_chapter_by_page(self, page: int) -> str:
        """페이지 번호로 챕터를 찾습니다."""
        chapter_pages = {
            "Chapter1 - 변수": (30, 107),
            "Chapter2 - 연산자": (108, 157),
            "Chapter3 - 조건문과 반복문": (158, 205),
            "Chapter4 - 배열": (206, 253),
            "Chapter5 - 객체지향 프로그래밍 I": (254, 339)
        }
        
        for chapter_name, (start, end) in chapter_pages.items():
            if start <= page <= end:
                return chapter_name
        
        return "기타"

class AnswerHistoryManager:
    """답변 기록 관리 클래스"""
    
    def __init__(self, history_file: str = "answer_history.json"):
        self.history_file = history_file
        self.history = self.load_history()
    
    def load_history(self) -> List[Dict[str, Any]]:
        """답변 기록을 로드합니다."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"⚠️ 답변 기록 로드 실패: {e}")
            return []
    
    def save_history(self) -> bool:
        """답변 기록을 저장합니다."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ 답변 기록 저장 실패: {e}")
            return False
    
    def add_answer(self, question: Dict[str, Any], user_answer: int, is_correct: bool):
        """답변을 기록합니다."""
        answer_record = {
            'timestamp': datetime.now().isoformat(),
            'question': question.get('question', ''),
            'user_answer': user_answer,
            'correct_answer': question.get('correct_answer', 0),
            'is_correct': is_correct,
            'chapter': question.get('chapter', ''),
            'difficulty': question.get('difficulty', '보통'),
            'concept_keywords': question.get('concept_keywords', [])
        }
        
        self.history.append(answer_record)
        self.save_history() 