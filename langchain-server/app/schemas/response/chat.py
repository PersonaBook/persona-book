from pydantic import BaseModel
from typing import Optional
from app.schemas.enum import Sender, MessageType, ChatState


class AiMessageResponse(BaseModel):
    userId: int  # 실제로는 long
    bookId: int  # 실제로는 long
    sender: Sender = Sender.AI
    content: str
    messageType: MessageType = MessageType.TEXT
    chatState: ChatState

    class Config:
        use_enum_values = True

class GeneratingQuestionResponse(BaseModel):
    userId: int  # 실제로는 long
    bookId: int  # 실제로는 long
    sender: Sender = Sender.AI
    content: str
    messageType: MessageType = MessageType.TEXT
    chatState: ChatState
    domain: Optional[str] = None
    concept: Optional[str] = None
    problemText: Optional[str] = None
    correctAnswer: Optional[str] = None