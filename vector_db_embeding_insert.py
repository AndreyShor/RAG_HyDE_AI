import os
import uuid
import requests
from typing import List
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from langchain.embeddings.base import Embeddings

# === CONFIGURATION ===
DOCUMENTS_DIR = "./text_output_random300"  # path to your .txt files
QDRANT_COLLECTION_NAME = "physics_papers_random_300_pages"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
EMBEDDING_DIM = 768  # Change this if your model returns a different dimension

API_MODEL_BAASE = "http://localhost:1234/v1"
API_MODEL_MODEL = "gemma-3-4b-it"  # or the exact model identifier LM Studio exposes
API_MODEL_API_KEY = "lm-studio"  # API key is not needed for local LM Studio server but LangChain requires something


class LMStudioEmbeddings(Embeddings):
    def __init__(self, api_base="http://localhost:1234/v1", model="gemma-3-4b-it", api_key="lm-studio"):
        self.api_base = api_base
        self.model = model
        self.api_key = api_key

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> List[float]:
        return self._embed(text)

    def _embed(self, text: str) -> List[float]:
        response = requests.post(
            f"{self.api_base}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}"
            },
            json={
                "model": self.model,
                "input": text
            }
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]


# === INITIALIZE QDRANT ===
client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

if not client.collection_exists(QDRANT_COLLECTION_NAME):
    client.recreate_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
    )

# === EMBEDDING FUNCTION ===
def get_embedding(text):
    embeddings = LMStudioEmbeddings(
        api_base=API_MODEL_BAASE,
        model= API_MODEL_MODEL,  # or the exact model identifier LM Studio exposes
        api_key=API_MODEL_API_KEY
    )

    return embeddings.embed_query(text)

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
