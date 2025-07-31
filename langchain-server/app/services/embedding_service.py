from typing import List
from app.core.config import settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings


class EmbeddingService:
    def __init__(self):
        self.embedding_model = settings.embedding_model_name
        self.gemini_api_key = settings.gemini_api_key
        self.embeddings = None
        self.embedding_dimension = 3072
        self._initialized = False

    async def ainitialize(self):
        if not self._initialized:
            try:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model=self.embedding_model, google_api_key=self.gemini_api_key
                )
                self._initialized = True
                print(
                    f"[EmbeddingService] Initialized with model: {self.embedding_model}"
                )
            except Exception as e:
                print(f"[EmbeddingService] Initialization error: {e}")
                raise

    def _ensure_initialized(self):
        if self.embeddings is None:
            try:
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    model=self.embedding_model, google_api_key=self.gemini_api_key
                )
                self._initialized = True
                print(
                    f"[EmbeddingService] Sync initialized with model: {self.embedding_model}"
                )
            except Exception as e:
                print(f"[EmbeddingService] Sync initialization error: {e}")
                raise

    async def _ensure_async_initialized(self):
        if not self._initialized:
            await self.ainitialize()

    async def get_embedding(self, text: str) -> List[float]:
        await self._ensure_async_initialized()

        if not text or not text.strip():
            print(
                "[EmbeddingService] Warning: Attempted to get embedding for empty text. Returning empty list."
            )
            return []

        try:
            embedding = await self.embeddings.aembed_query(text)
            print(
                f"[EmbeddingService] Generated embedding with dimension: {len(embedding)}"
            )
            return embedding
        except Exception as e:
            print(f"[EmbeddingService] Gemini embedding error: {e}")
            raise

    def get_embedding_sync(self, text: str) -> List[float]:
        self._ensure_initialized()

        if not text or not text.strip():
            print(
                "[EmbeddingService] Warning: Attempted to get embedding for empty text. Returning empty list."
            )
            return []

        try:
            return self.embeddings.embed_query(text)
        except Exception as e:
            print(f"[EmbeddingService] Gemini embedding error: {e}")
            raise

    async def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        await self._ensure_async_initialized()

        if not texts:
            return []

        try:
            return await self.embeddings.aembed_documents(texts)
        except Exception as e:
            print(f"[EmbeddingService] Batch embedding error: {e}")
            raise

    def get_embeddings_batch_sync(self, texts: List[str]) -> List[List[float]]:
        self._ensure_initialized()

        if not texts:
            return []

        try:
            return self.embeddings.embed_documents(texts)
        except Exception as e:
            print(f"[EmbeddingService] Batch embedding error: {e}")
            raise
