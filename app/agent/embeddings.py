from __future__ import annotations

from typing import List, Optional

from app.config.settings import load_api_settings


class EmbeddingService:
    def __init__(self, model_name: Optional[str] = None):
        settings = load_api_settings()
        self.model_name = model_name or settings.rag_embedding_model
        self._model = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed(self, texts: List[str]) -> List[List[float]]:
        model = self._load_model()
        vectors = model.encode(texts, convert_to_numpy=True)
        return [vec.tolist() for vec in vectors]

    def embed_query(self, text: str) -> List[float]:
        return self.embed([text])[0]
