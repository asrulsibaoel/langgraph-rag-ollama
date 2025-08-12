import os
import pandas as pd
from pymilvus import connections, Collection
from langchain_ollama import OllamaEmbeddings
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

import dotenv

dotenv.load_dotenv(".env")


# ===== CONFIG =====
CSV_FILE = os.getenv("BULK_INSERT_CSV_FILE", "data/medquad.csv")
URI = os.getenv(
    "MILVUS_URI", "https://in03-ccae31557aae495.serverless.gcp-us-west1.cloud.zilliz.com")
TOKEN = os.getenv("MILVUS_TOKEN", "")
COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "qwen3_documents")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "qwen3:8b")
BATCH_SIZE = int(os.getenv("BULK_INSERT_BATCH_SIZE", 32))
# tune this based on CPU cores
MAX_THREADS = int(os.getenv("MAX_THREADS", "4"))
# ==================

# 1. Connect to Zilliz
connections.connect(
    alias="default",
    uri=URI,
    token=TOKEN
)

# 2. Load CSV
df = pd.read_csv(CSV_FILE)

# Clean data
df = df.dropna(subset=["text"])
df["text"] = df["text"].astype(str)
df["source"] = df["source"].fillna("").astype(str)
df["category"] = df["category"].fillna("").astype(str)

# 3. Initialize embeddings
embeddings = OllamaEmbeddings(
    model=EMBED_MODEL,
    base_url=OLLAMA_URL
)

collection = Collection(COLLECTION_NAME)

# 4. Function for batch processing


def process_batch(batch_df):
    vectors = embeddings.embed_documents(batch_df["text"].tolist())
    ids = [str(uuid.uuid4()) for _ in range(len(batch_df))]
    data_to_insert = [
        ids,
        vectors,
        batch_df["text"].tolist(),
        batch_df["source"].tolist(),
        batch_df["category"].tolist()
    ]
    collection.insert(data_to_insert)
    return len(batch_df)


# 5. Threaded execution
futures = []

print(f"Starting bulk insert into collection '{COLLECTION_NAME}'...")
print(f"Using {MAX_THREADS} threads with batch size {BATCH_SIZE}...")
with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    for start in range(0, len(df), BATCH_SIZE):
        end = start + BATCH_SIZE
        batch_df = df.iloc[start:end]
        futures.append(executor.submit(process_batch, batch_df))

    # Progress tracking
    total_inserted = 0
    for future in tqdm(as_completed(futures), total=len(futures), desc="Embedding & Inserting"):
        total_inserted += future.result()
        tqdm.write(f"Inserted {total_inserted} rows so far...")

# 6. Final flush
collection.flush()

print(
    f"✅ Inserted {total_inserted} rows into collection '{COLLECTION_NAME}' using {MAX_THREADS} threads.")
