from pydantic import BaseModel
from app.schemas.enum import Sender, MessageType, ChatState


class UserMessageRequest(BaseModel):
    userId: int  # 실제로는 long
    bookId: int  # 실제로는 long
    sender: Sender = Sender.USER
    content: str
    messageType: MessageType = MessageType.TEXT
    chatState: ChatState

    class Config:
        use_enum_values = True
