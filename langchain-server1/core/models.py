"""
AI 모델 관리
"""

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

class ModelManager:
    """AI 모델 관리 클래스"""
    
    def __init__(self):
        self.llm = None
        self.embeddings = None
    
    def initialize_models(self) -> bool:
        """AI 모델들을 초기화합니다."""
        try:
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
            self.llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
            return True
        except Exception as e:
            print(f"❌ AI 모델 초기화 실패: {e}")
            return False
    
    def get_llm(self):
        """LLM을 반환합니다."""
        return self.llm
    
    def get_embeddings(self):
        """임베딩 모델을 반환합니다."""
        return self.embeddings 