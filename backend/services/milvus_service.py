# services/milvus_service.py
from pymilvus import connections, Collection
from langchain_ollama import OllamaEmbeddings

from backend.settings import settings

# Connect to Milvus
connections.connect(
    alias="default",
    uri=settings.milvus_uri,
    token=settings.milvus_token
)

collection = Collection(settings.milvus_collection_name)

# Embedding model
embeddings = OllamaEmbeddings(
    model=settings.ollama_embed_model,
    base_url=settings.ollama_url
)


def search_context(query: str, top_k: int = 3) -> str:
    """Retrieve top-k most relevant context from Milvus."""
    query_vector = embeddings.embed_query(query)
    results = collection.search(
        data=[query_vector],
        anns_field="vector",
        param={"metric_type": "COSINE", "params": {"nprobe": 10}},
        limit=top_k,
        output_fields=["text", "source", "category"]
    )

    if not results or not results[0]:
        return ""

    context_parts = []
    for hit in results[0]:
        row = hit.entity
        context_parts.append(
            f"{row['text']} (Source: {row['source']}, Category: {row['category']})")

    return "\n\n".join(context_parts)
