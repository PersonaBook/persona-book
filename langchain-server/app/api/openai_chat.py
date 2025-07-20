from fastapi import APIRouter, HTTPException
from app.schemas.openai_chat import OpenAIChatRequest, OpenAIChatResponse
from app.services.openai_service import openai_service

router = APIRouter()

@router.post("/openai-chat", response_model=OpenAIChatResponse)
def openai_chat(req: OpenAIChatRequest):
    try:
        answer = openai_service.ask_openai(req)
        return OpenAIChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 