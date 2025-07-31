from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class LearningMaterial:
    concept: str
    content_text: str
    url: str
    title: str
    id: Optional[str] = None
    content_embedding: List[float] = field(default_factory=list)
    material_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    source: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def to_elasticsearch_doc(self) -> Dict:
        doc = self.__dict__.copy()
        if "created_at" in doc and isinstance(doc["created_at"], datetime):
            doc["created_at"] = doc["created_at"].isoformat() + "Z"
        if "updated_at" in doc and isinstance(doc["updated_at"], datetime):
            doc["updated_at"] = doc["updated_at"].isoformat() + "Z"
        if "id" in doc:
            del doc["id"]
        if "score" in doc:
            del doc["score"]
        return doc

    @classmethod
    def from_elasticsearch_doc(cls, doc_id: str, doc_source: Dict):
        if "created_at" in doc_source and isinstance(doc_source["created_at"], str):
            doc_source["created_at"] = datetime.fromisoformat(
                doc_source["created_at"].replace("Z", "")
            )
        if "updated_at" in doc_source and isinstance(doc_source["updated_at"], str):
            doc_source["updated_at"] = datetime.fromisoformat(
                doc_source["updated_at"].replace("Z", "")
            )
        return cls(id=doc_id, **doc_source)
