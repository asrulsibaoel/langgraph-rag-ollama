from backend.milvus_client import get_embeddings

embedding = get_embeddings(provider="ollama", embedding_model="qwen3:8b")

text = "Hello, how are you?"
vector = embedding.embed_query(text)
print(f"Length of the vector: {len(vector)}")
