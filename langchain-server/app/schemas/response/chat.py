from app.schemas.request.chat import FeatureContext, StageContext
from pydantic import BaseModel


class AiMessageResponse(BaseModel):
    userId: str
    bookId: int
    sender: str = "AI"
    content: str
    messageType: str = "TEXT"
    featureContext: FeatureContext
    stageContext: StageContext
