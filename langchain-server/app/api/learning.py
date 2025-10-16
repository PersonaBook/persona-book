from app.repository.learning_material_repository import LearningMaterialRepository
from app.schemas.request.learning import ExplanationRequest, ConceptExplanationRequest
from app.schemas.response.learning import (
    ExplanationApiResponse,
    ConceptExplanationApiResponse,
    ConceptExplanationResult
)
from app.services.learning_service import LearningService
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_learning_material_repository
from app.agents.learning_agent import LearningAgent
import traceback

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


@router.post(
    "/explanation",
    response_model=ExplanationApiResponse,
    status_code=status.HTTP_200_OK,
)
async def get_explanation(
    request: ExplanationRequest,
    learning_service: LearningService = Depends(get_learning_service),
    learning_agent: LearningAgent = Depends(get_learning_agent),
):
    try:
        print("🟢 재설명 요청 받음:", request.dict())
        preprocessed_data = await learning_service.preprocess_learning_request(request)
        agent_result = await learning_agent.run(preprocessed_data)

        return {
            "message": "Explanation generation process completed",
            "result": agent_result,
        }
    except Exception as e:
        print("🔥 예외 발생:", repr(e))
        traceback.print_exc()  # 전체 traceback 출력
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during explanation generation: {e}",
        )


@router.post(
    "/concept-explanation",
    response_model=ConceptExplanationApiResponse,
    status_code=status.HTTP_200_OK,
)
async def get_concept_explanation(
    request: ConceptExplanationRequest,
    learning_service: LearningService = Depends(get_learning_service),
):
    """
    개념 설명 API (초기 설명용)

    - 사용자가 입력한 개념에 대해 RAG 기반 설명 생성
    - 재설명 API(/learning/explanation)와 달리 간단한 요청 구조
    """
    try:
        print(f"🟢 개념 설명 요청: {request.content}")

        # 개념 설명 생성
        explanation = await learning_service.generate_concept_explanation(
            concept=request.content,
            user_experience_level=request.user_experience_level
        )

        return ConceptExplanationApiResponse(
            message="Concept explanation generated successfully",
            result=ConceptExplanationResult(
                explanation=explanation,
                concept=request.content
            )
        )
    except Exception as e:
        print(f"🔥 개념 설명 생성 실패: {repr(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during concept explanation: {e}",
        )
