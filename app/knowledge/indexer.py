from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from app.agent.embeddings import EmbeddingService
from app.config.settings import load_api_settings
from app.knowledge.chunks import chunk_text
from app.knowledge.loader import iter_files, load_text_files
from app.knowledge.vector_store import build_vector_store


class KnowledgeIndexer:
    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
    ):
        settings = load_api_settings()
        self.embedding_service = embedding_service or EmbeddingService(settings.rag_embedding_model)
        self.vector_store = build_vector_store()
        self.chunk_size = settings.rag_chunk_size
        self.chunk_overlap = settings.rag_chunk_overlap

    def index_path(self, root: Path, tenant_id: str = "default") -> int:
        files = list(iter_files(root))
        documents = load_text_files(files)
        return self.index_documents(documents, tenant_id=tenant_id)

    def index_documents(self, documents: Dict[str, str], tenant_id: str = "default") -> int:
        chunks: List[str] = []
        metadata_list: List[Dict[str, str]] = []
        for source, content in documents.items():
            for chunk in chunk_text(content, max_chars=self.chunk_size, overlap=self.chunk_overlap):
                chunks.append(chunk)
                metadata_list.append({"source": source})

        if not chunks:
            return 0

        embeddings = self.embedding_service.embed(chunks)
        items = [
            (embedding, chunk, metadata)
            for embedding, chunk, metadata in zip(embeddings, chunks, metadata_list)
        ]
        self.vector_store.add(tenant_id, items)
        return len(items)
