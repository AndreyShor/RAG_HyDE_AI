from fastapi import FastAPI # type: ignore
from pymongo import MongoClient
from qdrant_client import QdrantClient # type: ignore
from qdrant_client.http.exceptions import UnexpectedResponse # type: ignore
import os
import uuid

app = FastAPI()

# Setup database connections
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
QDRANT_HOST = os.getenv("QDRANT_HOST", "http://qdrant:6333")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["test_db"]
mongo_collection = mongo_db["test1"]

qdrant_client = QdrantClient(url=QDRANT_HOST)
QDRANT_COLLECTION = "test1"

@app.on_event("startup")
def setup_databases():
    # Ensure MongoDB has a test document
    if mongo_collection.count_documents({}) == 0:
        mongo_collection.insert_one({"name": "Test Document", "value": 42})

    # Ensure Qdrant has a test collection and vector
    collections = [col.name for col in qdrant_client.get_collections().collections]
    if QDRANT_COLLECTION not in collections:
        qdrant_client.recreate_collection(
            collection_name=QDRANT_COLLECTION,
            vectors_config=VectorParams(size=3, distance=Distance.COSINE)
        )
        # Insert one point
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=[0.1, 0.2, 0.3],
                    payload={"source": "test"}
                )
            ]
        )

@app.get("/test-data")
def get_test_data():
    # Fetch Mongo document
    mongo_doc = mongo_collection.find_one({}, {"_id": 0})

    # Fetch Qdrant vector
    qdrant_points = qdrant_client.scroll(
        collection_name=QDRANT_COLLECTION,
        limit=1,
        with_payload=True
    )
    qdrant_point = qdrant_points[0][0] if qdrant_points[0] else {}

    return {
        "mongo": mongo_doc,
        "qdrant": {
            "id": qdrant_point.id if qdrant_point else None,
            "vector": qdrant_point.vector if qdrant_point else [],
            "payload": qdrant_point.payload if qdrant_point else {}
        }
    }
