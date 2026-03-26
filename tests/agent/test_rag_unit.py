from app.agent.rag import RAGService
from app.knowledge.vector_store import InMemoryVectorStore, DocumentChunk


class FakeEmbeddingService:
    def embed(self, texts):
        vectors = []
        for text in texts:
            if "doc1" in text:
                vectors.append([1.0, 0.0])
            else:
                vectors.append([0.0, 1.0])
        return vectors

    def embed_query(self, text):
        return [1.0, 0.0]


def test_rag_search_filters_by_score():
    embedding = FakeEmbeddingService()
    rag = RAGService(embedding_service=embedding)
    rag.vector_store = InMemoryVectorStore()
    rag.top_k = 5
    rag.min_score = 0.5

    rag.vector_store.add(
        "default",
        [
            ([1.0, 0.0], "doc1 content", {"source": "doc1"}),
            ([0.0, 1.0], "doc2 content", {"source": "doc2"}),
        ],
    )

    results = rag.search("consulta", tenant_id="default")
    assert len(results) == 1
    assert results[0].content == "doc1 content"


def test_rag_generate_returns_none_when_llm_disabled():
    rag = RAGService(embedding_service=FakeEmbeddingService())
    rag.llm_enabled = False
    docs = [DocumentChunk(content="info", metadata={}, score=0.9)]
    assert rag.generate_with_context("pregunta", docs) is None
