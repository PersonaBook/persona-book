from app.schemas.request.openai_chat import OpenAIChatRequest
from app.schemas.response.openai_chat import OpenAIChatResponse
from app.services.openai_service import openai_service
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.post("/openai-chat", response_model=OpenAIChatResponse)
def openai_chat(req: OpenAIChatRequest):
    try:
        answer = openai_service.ask_openai(req)
        return OpenAIChatResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
