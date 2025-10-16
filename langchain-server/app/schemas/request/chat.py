from pydantic import BaseModel, field_validator
from app.schemas.enum import Sender, MessageType, ChatState


class UserMessageRequest(BaseModel):
    userId: int  # 실제로는 long
    bookId: int  # 실제로는 long
    sender: Sender = Sender.USER
    content: str
    messageType: MessageType = MessageType.TEXT
    chatState: ChatState

    @field_validator('content')
    @classmethod
    def validate_content(cls, v):
        if isinstance(v, bytes):
            # 바이트인 경우 안전하게 UTF-8로 디코딩
            try:
                return v.decode('utf-8')
            except UnicodeDecodeError:
                # UTF-8 디코딩 실패 시 에러 무시하고 디코딩
                return v.decode('utf-8', errors='ignore')
        elif isinstance(v, str):
            # 문자열인 경우 안전하게 인코딩 후 재디코딩
            try:
                return v.encode('utf-8').decode('utf-8')
            except UnicodeDecodeError:
                return v.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        return str(v)

    class Config:
        use_enum_values = True

