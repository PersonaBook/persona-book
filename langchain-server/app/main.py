from fastapi import FastAPI
from app.api.openai_chat import router as openai_chat_router

app = FastAPI()

app.include_router(openai_chat_router, prefix="/api/v1") 