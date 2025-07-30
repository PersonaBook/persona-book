from app.repository.learning_material_repository import LearningMaterialRepository
from app.schemas.request.learning import ExplanationRequest
from app.services.learning_service import LearningService
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_learning_material_repository
from app.agents.learning_agent import LearningAgent

router = APIRouter()


def get_learning_service(
    repo: LearningMaterialRepository = Depends(get_learning_material_repository),
) -> LearningService:
    return LearningService(repo)


async def get_learning_agent(
    learning_service: LearningService = Depends(get_learning_service),
) -> LearningAgent:
    agent = LearningAgent(learning_service)
    await agent.ainitialize()
    return agent


@router.post("/explanation", status_code=status.HTTP_200_OK)
async def get_explanation(
    request: ExplanationRequest,
    learning_service: LearningService = Depends(get_learning_service),
    learning_agent: LearningAgent = Depends(get_learning_agent),
):
    try:
        preprocessed_data = await learning_service.preprocess_learning_request(request)
        agent_result = await learning_agent.run(preprocessed_data)

        return {
            "message": "Explanation generation process completed",
            "result": agent_result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during explanation generation: {e}",
        )
