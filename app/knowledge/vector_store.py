from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import math

from app.config.settings import load_api_settings


@dataclass
class DocumentChunk:
    content: str
    metadata: Dict[str, Any]
    score: float = 0.0


class VectorStore:
    def add(self, tenant_id: str, items: List[Tuple[List[float], str, Dict[str, Any]]]) -> None:
        raise NotImplementedError

    def query(self, tenant_id: str, embedding: List[float], top_k: int = 5) -> List[DocumentChunk]:
        raise NotImplementedError


class InMemoryVectorStore(VectorStore):
    def __init__(self):
        self._data: Dict[str, List[Tuple[List[float], str, Dict[str, Any]]]] = {}

    def add(self, tenant_id: str, items: List[Tuple[List[float], str, Dict[str, Any]]]) -> None:
        bucket = self._data.setdefault(tenant_id, [])
        bucket.extend(items)

    def query(self, tenant_id: str, embedding: List[float], top_k: int = 5) -> List[DocumentChunk]:
        items = self._data.get(tenant_id, [])
        results: List[DocumentChunk] = []
        for vector, content, metadata in items:
            score = _cosine_similarity(embedding, vector)
            results.append(DocumentChunk(content=content, metadata=metadata, score=score))
        results.sort(key=lambda d: d.score, reverse=True)
        return results[:top_k]


class PostgresVectorStore(VectorStore):
    def __init__(self, database_url: str, embedding_dim: int):
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        from app.database.models import KnowledgeDocument

        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)
        self.KnowledgeDocument = KnowledgeDocument
        self.embedding_dim = embedding_dim

    def add(self, tenant_id: str, items: List[Tuple[List[float], str, Dict[str, Any]]]) -> None:
        session = self.Session()
        try:
            for vector, content, metadata in items:
                doc = self.KnowledgeDocument(
                    tenant_id=tenant_id,
                    content=content,
                    extra_metadata=metadata,
                    embedding=vector,
                )
                session.add(doc)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def query(self, tenant_id: str, embedding: List[float], top_k: int = 5) -> List[DocumentChunk]:
        session = self.Session()
        try:
            results = (
                session.query(self.KnowledgeDocument)
                .filter(self.KnowledgeDocument.tenant_id == tenant_id)
                .order_by(self.KnowledgeDocument.embedding.cosine_distance(embedding))
                .limit(top_k)
                .all()
            )
            return [
                DocumentChunk(
                    content=row.content,
                    metadata=row.extra_metadata or {},
                    score=1.0 - (row.embedding.cosine_distance(embedding) or 0.0),
                )
                for row in results
            ]
        finally:
            session.close()


def build_vector_store() -> VectorStore:
    settings = load_api_settings()
    if settings.rag_use_postgres and settings.is_postgres_enabled():
        return PostgresVectorStore(settings.database_url, settings.rag_embedding_dim)
    return InMemoryVectorStore()


def _cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
