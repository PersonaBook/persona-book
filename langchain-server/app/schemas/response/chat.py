from pydantic import BaseModel
from app.schemas.request.chat import FeatureContext, StageContext

class AiMessageResponse(BaseModel):
    userId: str
    bookId: int
    sender: str = "AI"
    content: str
    messageType: str = "TEXT"
    featureContext: FeatureContext
    stageContext: StageContext 