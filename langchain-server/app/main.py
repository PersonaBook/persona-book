from contextlib import asynccontextmanager

from app.api.learning import router as learning_router

from app.api.question_generator import router as question_generator_router
from app.core.elasticsearch_client import ElasticsearchClient
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.tools.learning_material_search_tool import get_learning_material_search_tool
from app.tools.google_search_tool import get_google_search_tool
from app.tools.explanation_generator_tool import get_explanation_generator_tool
from app.agents.learning_agent import LearningAgent
from app.repository.learning_material_repository import LearningMaterialRepository
from app.services.learning_service import LearningService
from app.services.embedding_service import EmbeddingService


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ElasticsearchClient.initialize()

    es_client = await ElasticsearchClient.get_client()
    embedding_service = EmbeddingService()
    await embedding_service.ainitialize()
    learning_material_repo = LearningMaterialRepository(es_client, embedding_service)
    await learning_material_repo.create_index()
    learning_service = LearningService(learning_material_repo)

    app.state.learning_material_search_tool = await get_learning_material_search_tool()
    app.state.google_search_tool = await get_google_search_tool()
    app.state.explanation_generator_tool = await get_explanation_generator_tool()

    app.state.learning_agent = LearningAgent(learning_service)
    await app.state.learning_agent.ainitialize()

    yield
    await ElasticsearchClient.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    learning_router, prefix="/api/v1/learning", tags=["Learning Materials"]
)
app.include_router(question_generator_router, prefix="/api/v1")
