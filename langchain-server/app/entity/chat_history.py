from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ChatHistory:
    """채팅 이력 도메인 엔티티"""

    age: int
    background: str
    feedback: str
    question: str
    answer: str
    model_name: str
    id: Optional[str] = None
    created_at: Optional[datetime] = field(default_factory=datetime.now)

    def __post_init__(self):
        """데이터 검증 및 초기화"""
        self._validate_data()

    def _validate_data(self):
        """데이터 검증 로직"""
        if self.age < 0 or self.age > 120:
            raise ValueError("나이는 0-120 사이여야 합니다")

        if not self.question.strip():
            raise ValueError("질문은 비어있을 수 없습니다")

        if not self.answer.strip():
            raise ValueError("답변은 비어있을 수 없습니다")

        if not self.background.strip():
            raise ValueError("배경은 비어있을 수 없습니다")

    def is_recent(self, days: int = 7) -> bool:
        """최근 N일 내의 이력인지 확인"""
        if not self.created_at:
            return False
        return (datetime.now() - self.created_at).days <= days

    def get_difficulty_level(self) -> str:
        """난이도 레벨 반환"""
        if self.age < 20:
            return "초급"
        elif self.age < 30:
            return "중급"
        else:
            return "고급"

    def get_age_group(self) -> str:
        """연령대 반환"""
        if self.age < 10:
            return "어린이"
        elif self.age < 20:
            return "청소년"
        elif self.age < 30:
            return "20대"
        elif self.age < 40:
            return "30대"
        elif self.age < 50:
            return "40대"
        else:
            return "50대 이상"

    def to_elasticsearch_doc(self) -> dict:
        """Elasticsearch 문서로 변환"""
        return {
            "age": self.age,
            "background": self.background,
            "feedback": self.feedback,
            "question": self.question,
            "answer": self.answer,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "model_name": self.model_name,
        }

    @classmethod
    def from_elasticsearch_doc(cls, doc_id: str, source: dict) -> "ChatHistory":
        """Elasticsearch 문서에서 엔티티 생성"""
        return cls(
            id=doc_id,
            age=source["age"],
            background=source["background"],
            feedback=source["feedback"],
            question=source["question"],
            answer=source["answer"],
            created_at=(
                datetime.fromisoformat(source["created_at"])
                if source["created_at"]
                else None
            ),
            model_name=source["model_name"],
        )
