from app.api.chat import router as chat_router
from app.api.chat_history import router as chat_history_router
from app.api.openai_chat import router as openai_chat_router
from app.api.question_generator import router as question_generator_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")
app.include_router(openai_chat_router, prefix="/api/v1")
app.include_router(chat_history_router, prefix="/api/v1")
app.include_router(question_generator_router, prefix="/api/v1")
