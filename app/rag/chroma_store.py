"""
Chroma vector store with hybrid search + reranking.
Collections: objection_library, policy_documents, regulatory_guidelines
Embedding: models/text-embedding-004 via Google Generative AI
"""
import os
import chromadb
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.core.config import get_settings
import os
from dotenv import load_dotenv
load_dotenv()

settings = get_settings()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_chroma_client: Optional[chromadb.Client] = None


def get_chroma_client() -> chromadb.Client:
    global _chroma_client
    if _chroma_client is None:
        os.makedirs(settings.chroma_db_path, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=settings.chroma_db_path)
    return _chroma_client


class GeminiEmbeddingFunction(chromadb.EmbeddingFunction):
    """Custom embedding function using Google text-embedding-004"""

    def __call__(self, input: chromadb.Documents) -> chromadb.Embeddings:
        embeddings = []
        for text in input:
            try:
                result = genai.embed_content(
                    model=settings.embedding_model,
                    content=text,
                    task_type="retrieval_document"
                )
            except Exception as e:
                print(f"[RAG] Warning: {settings.embedding_model} failed, falling back to gemini-embedding-001. Error: {e}")
                result = genai.embed_content(
                    model="models/gemini-embedding-001",
                    content=text,
                    task_type="retrieval_document"
                )
            embeddings.append(result["embedding"])
        return embeddings


def get_query_embedding(text: str) -> List[float]:
    try:
        result = genai.embed_content(
            model=settings.embedding_model,
            content=text,
            task_type="retrieval_query"
        )
    except Exception as e:
        print(f"[RAG] Warning: {settings.embedding_model} failed, falling back to gemini-embedding-001. Error: {e}")
        result = genai.embed_content(
            model="models/gemini-embedding-001",
            content=text,
            task_type="retrieval_query"
        )
    return result["embedding"]


def get_collection(name: str) -> chromadb.Collection:
    client = get_chroma_client()
    return client.get_or_create_collection(
        name=name,
        embedding_function=GeminiEmbeddingFunction()
    )


def hybrid_search_and_rerank(
    collection_name: str,
    query: str,
    n_results: int = 5,
    metadata_filter: Optional[Dict] = None,
    rerank_top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Hybrid search: vector similarity + keyword matching.
    Reranking: score fusion of semantic similarity + BM25-style keyword overlap.
    """
    collection = get_collection(collection_name)

    # Vector search
    query_embedding = get_query_embedding(query)
    search_kwargs = {
        "query_embeddings": [query_embedding],
        "n_results": min(n_results, collection.count() or 1),
        "include": ["documents", "metadatas", "distances"]
    }
    if metadata_filter:
        search_kwargs["where"] = metadata_filter

    results = collection.query(**search_kwargs)

    if not results["documents"] or not results["documents"][0]:
        return []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # Keyword overlap scoring (BM25-style approximation)
    query_tokens = set(query.lower().split())
    scored = []
    for doc, meta, dist in zip(documents, metadatas, distances):
        doc_tokens = set(doc.lower().split())
        keyword_score = len(query_tokens & doc_tokens) / max(len(query_tokens), 1)
        semantic_score = 1 - dist  # cosine distance -> similarity
        # Fused score: 70% semantic + 30% keyword
        fused_score = 0.7 * semantic_score + 0.3 * keyword_score
        scored.append({
            "document": doc,
            "metadata": meta,
            "semantic_score": round(semantic_score, 4),
            "keyword_score": round(keyword_score, 4),
            "fused_score": round(fused_score, 4)
        })

    # Rerank by fused score
    scored.sort(key=lambda x: x["fused_score"], reverse=True)
    return scored[:rerank_top_k]


def add_documents(
    collection_name: str,
    documents: List[str],
    metadatas: List[Dict],
    ids: List[str]
):
    """Add or upsert documents to a Chroma collection."""
    collection = get_collection(collection_name)
    collection.upsert(documents=documents, metadatas=metadatas, ids=ids)


def init_chroma():
    """Initialize all collections (creates if not exists)."""
    collections = ["objection_library", "policy_documents", "regulatory_guidelines"]
    for name in collections:
        get_collection(name)
    print(f"[RAG] Chroma initialized with collections: {collections}")
