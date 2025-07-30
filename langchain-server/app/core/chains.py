"""
체인 파이프라인 관리
"""

class ChainFactory:
    """체인 시스템 생성 팩토리"""
    @staticmethod
    def create_complete_chain_system(llm, retriever):
        # 실제로는 LangChain의 다양한 체인 조합을 생성
        # 여기서는 단순히 래퍼 객체 반환
        class ChainExecutor:
            def __init__(self, llm, retriever):
                self.llm = llm
                self.retriever = retriever
        return None, ChainExecutor(llm, retriever) 