import os
import uuid
import requests
from typing import List
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from langchain.embeddings.base import Embeddings
from sentence_transformers import SentenceTransformer

# === CONFIGURATION ===

DOCUMENTS_DIR = os.path.dirname(__file__) + "/text_output_random300"
QDRANT_COLLECTION_NAME = "physics_papers_random_300_pages_v2"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
EMBEDDING_DIM = 384 


# === INITIALIZE QDRANT ===
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

if not client.collection_exists(QDRANT_COLLECTION_NAME):
    client.recreate_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
    )

# === EMBEDDING FUNCTION ===
def get_embedding(text):
    embedder = SentenceTransformer('all-MiniLM-L6-v2')  # Small and fast

    return embedder.encode(text).tolist()

# === PROCESSING FUNCTION ===
def process_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    if not content.strip():  # Skip empty files
        return None
    embedding = get_embedding(content)
    return PointStruct(
        id=str(uuid.uuid4()),
        vector=embedding,
        payload={
            "text": content,
            "source_file": os.path.basename(file_path)
        }
    )

# === PROCESS ALL FILES ===
all_txt_files = [os.path.join(DOCUMENTS_DIR, f) for f in os.listdir(DOCUMENTS_DIR) if f.endswith(".txt")]
points_to_insert = []

for file_path in tqdm(all_txt_files, desc="Processing pages"):
    try:
        point = process_file(file_path)
        if point:
            points_to_insert.append(point)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

# === BATCH INSERT TO QDRANT ===
BATCH_SIZE = 64
for i in range(0, len(points_to_insert), BATCH_SIZE):
    batch = points_to_insert[i:i + BATCH_SIZE]
    client.upsert(collection_name=QDRANT_COLLECTION_NAME, points=batch)
