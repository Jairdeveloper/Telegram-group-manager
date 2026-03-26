from __future__ import annotations

from typing import List, Optional

from app.agent.embeddings import EmbeddingService
from app.config.settings import load_api_settings
from app.knowledge.vector_store import DocumentChunk, build_vector_store
from app.monitoring.agent_metrics import record_llm_usage, record_rag_latency
from chat_service.llm.factory import LLMFactory, config_from_settings
from chat_service.llm.base import LLMError
import time


class RAGService:
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        settings = load_api_settings()
        self.embedding_service = embedding_service or EmbeddingService(settings.rag_embedding_model)
        self.vector_store = build_vector_store()
        self.top_k = settings.rag_top_k
        self.min_score = settings.rag_min_score
        self.llm_enabled = settings.llm_enabled
        self.llm_config = config_from_settings(settings)

    def search(self, query: str, tenant_id: str = "default") -> List[DocumentChunk]:
        start = time.time()
        embedding = self.embedding_service.embed_query(query)
        results = self.vector_store.query(tenant_id, embedding, top_k=self.top_k)
        filtered = [r for r in results if r.score >= self.min_score]
        record_rag_latency(tenant_id, time.time() - start)
        return filtered

    def generate_with_context(self, query: str, docs: List[DocumentChunk]) -> Optional[str]:
        if not docs:
            return None
        context = "\n\n".join(doc.content for doc in docs[: self.top_k])
        prompt = (
            "Usa la siguiente informacion para responder la pregunta. "
            "Si no es suficiente, responde que no tienes datos.\n\n"
            f"Contexto:\n{context}\n\n"
            f"Pregunta: {query}"
        )
        if not self.llm_enabled:
            return None
        try:
            provider = LLMFactory.get_provider(self.llm_config)
            response = provider.generate(prompt)
            if response:
                record_llm_usage(
                    provider=self.llm_config.provider,
                    model=self.llm_config.model,
                    prompt=prompt,
                    response=response,
                    source="rag",
                )
            return response
        except LLMError:
            return None
