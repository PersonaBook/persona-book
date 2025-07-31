from typing import List, Dict, Any
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool
from langchain.agents import AgentExecutor, create_react_agent
from app.schemas.request.learning import ExplanationRequest
from app.schemas.tool_input import (
    LearningMaterialSearchToolInput,
    LowUnderstandingAttemptSummaryTool,
    GoogleSearchToolInput,
    ExplanationGeneratorToolInput,
)
from app.schemas.response.learning import LearningMaterialSearchResult
from app.services.learning_service import LearningService
from app.tools.learning_material_search_tool import get_learning_material_search_tool
from app.tools.google_search_tool import get_google_search_tool
from app.tools.explanation_generator_tool import get_explanation_generator_tool
from app.core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI


class LearningAgent:
    def __init__(self, learning_service: LearningService):
        self.learning_service = learning_service
        self.llm = self._initialize_llm()
        self.tools = []
        self.agent_executor = None

    def _initialize_llm(self):
        return ChatGoogleGenerativeAI(
            model=settings.gemini_model_name, google_api_key=settings.gemini_api_key
        )

    async def ainitialize(self):
        self.tools = await self._initialize_tools()
        self.agent_executor = self._create_agent_executor()

    async def _initialize_tools(self) -> List[BaseTool]:
        return [
            await get_learning_material_search_tool(),
            await get_google_search_tool(),
            await get_explanation_generator_tool(),
        ]

    def _create_agent_executor(self) -> AgentExecutor:
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are an AI tutor designed to help users understand concepts. "
                    "Use the provided tools to search for learning materials and generate explanations."
                    "If initial search results are insufficient, use GoogleSearchTool to find more resources.",
                ),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
                MessagesPlaceholder(variable_name="tools"),
                MessagesPlaceholder(variable_name="tool_names"),
            ]
        )

        agent = create_react_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True
        )

    async def run(self, preprocessed_data: ExplanationRequest) -> Dict[str, Any]:
        agent_input = {
            "input": f"Find learning materials for the concept: {preprocessed_data.problem_info.concept}. "
            f"User's learning experience: {preprocessed_data.user_info.learning_experience}. "
            f"Problem text: {preprocessed_data.problem_info.problem_text}. "
            f"Previous failed attempts: {preprocessed_data.low_understanding_attempts_summary}. "
            f"Best previous explanation: {preprocessed_data.best_attempt_text}.",
            "intermediate_steps": [],
        }

        learning_search_tool_input = LearningMaterialSearchToolInput(
            user_info=preprocessed_data.user_info,
            low_understanding_attempts_summary=[
                LowUnderstandingAttemptSummaryTool(**s.dict())
                for s in preprocessed_data.low_understanding_attempts_summary
            ],
            best_attempt_text=preprocessed_data.best_attempt_text,
            problem_info=preprocessed_data.problem_info,
        )

        initial_search_results: List[LearningMaterialSearchResult] = await self.tools[
            0
        ].arun(
            {
                "user_info": learning_search_tool_input.user_info.dict(),
                "low_understanding_attempts_summary": [
                    s.dict()
                    for s in learning_search_tool_input.low_understanding_attempts_summary
                ],
                "best_attempt_text": learning_search_tool_input.best_attempt_text,
                "problem_info": learning_search_tool_input.problem_info.dict(),
            }
        )
        final_learning_materials = initial_search_results

        if not initial_search_results:
            google_tool_input = GoogleSearchToolInput(
                concept=preprocessed_data.problem_info.concept,
                domain=preprocessed_data.problem_info.domain,
            )
            google_search_results: List[
                LearningMaterialSearchResult
            ] = await self.tools[1].arun(
                {
                    "concept": google_tool_input.concept,
                    "domain": google_tool_input.domain,
                }
            )

            final_search_results: List[LearningMaterialSearchResult] = await self.tools[
                0
            ].arun(
                {
                    "user_info": learning_search_tool_input.user_info.dict(),
                    "low_understanding_attempts_summary": [
                        s.dict()
                        for s in learning_search_tool_input.low_understanding_attempts_summary
                    ],
                    "best_attempt_text": learning_search_tool_input.best_attempt_text,
                    "problem_info": learning_search_tool_input.problem_info.dict(),
                }
            )
            final_learning_materials = final_search_results

        explanation_tool_input = ExplanationGeneratorToolInput(
            learning_materials=[mat.dict() for mat in final_learning_materials],
            user_info=preprocessed_data.user_info,
            problem_info=preprocessed_data.problem_info,
            low_understanding_attempts_summary=[
                s.dict() for s in preprocessed_data.low_understanding_attempts_summary
            ],
            best_attempt_text=preprocessed_data.best_attempt_text,
        )
        generated_explanation: str = await self.tools[2].arun(
            {
                "learning_materials": explanation_tool_input.learning_materials,
                "user_info": explanation_tool_input.user_info.dict(),
                "problem_info": explanation_tool_input.problem_info.dict(),
                "low_understanding_attempts_summary": explanation_tool_input.low_understanding_attempts_summary,
                "best_attempt_text": explanation_tool_input.best_attempt_text,
            }
        )

        return {"explanation": generated_explanation}
