import os
from dotenv import load_dotenv

from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    milvus_uri: str = os.getenv(
        "MILVUS_URI", "https://in03-ccae31557aae495.serverless.gcp-us-west1.cloud.zilliz.com")
    vector_db_cluster_name: str = os.getenv(
        "MILVUS_CLUSTER_NAME", "cakrul-cv")
    milvus_collection_name: str = os.getenv(
        "MILVUS_COLLECTION_NAME", "qwen3_documents")
    milvus_token: str = os.getenv("MILVUS_TOKEN", "")
    bulk_insert_max_threads: int = int(os.getenv("MAX_THREADS", "4"))
    bulk_insert_batch_size: int = int(os.getenv("BULK_INSERT_BATCH_SIZE", 32))
    bulk_insert_csv_file: str = os.getenv(
        "BULK_INSERT_CSV_FILE", "data/medquad.csv")
    ollama_url: str = os.getenv(
        "OLLAMA_URL", "http://localhost:11434")
    ollama_embed_model: str = os.getenv(
        "OLLAMA_EMBED_MODEL", "qwen3:8b")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()


__all__ = ["settings"]
