from fastapi import FastAPI # type: ignore

from typing import List
from pydantic import BaseModel

from pymongo import MongoClient
from qdrant_client import QdrantClient # type: ignore
from qdrant_client.http.exceptions import UnexpectedResponse # type: ignore
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# LLM Setings
local_api_base = "http://host.docker.internal:1234/v1"
local_api_key = "lm-studio"
model_name = "gemma-3-4b-it" 

app = FastAPI()


# 👇 Add this block before your routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ], # or ["*"] for all origins (dev only)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Setup database connections
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongodb:27017")
QDRANT_HOST = os.getenv("QDRANT_HOST", "http://qdrant:6333")

mongo_client = MongoClient(MONGO_URI)
mongo_db = mongo_client["test_db"]
mongo_collection = mongo_db["test1"]

qdrant_client = QdrantClient(url=QDRANT_HOST)
QDRANT_COLLECTION = "test1"

@app.get("/start")
async def root():
    return {"message": "Hello World"}


class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: float

@app.post("/", )
async def send_llm_request(request: ChatRequest):
    print(request.messages[-1].content)

    lastMessage = request.messages[-1].content

    llm = ChatOpenAI(
        model=model_name,
        openai_api_key=local_api_key,
        openai_api_base=local_api_base,
        temperature=0.7 # Adjust temperature and other parameters as needed
    )

    output_parser = StrOutputParser()

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant, your name is Jarvis. Please provide short answers."),
        ("user", "{input}")
    ])

    chain = prompt | llm | output_parser

    response = chain.invoke({"input": lastMessage})

    try:
        print("\nSending prompt to local LLM via LangChain...")
        response = chain.invoke({"input": lastMessage})
        print("\nResponse:")
        print(response)
    except Exception as e:
        print(f"\nAn error occurred:")
        print(e)
        print("\nTroubleshooting tips:")
        print("- Is the LM Studio server running?")
        print("- Is the correct model loaded in LM Studio?")
        print(f"- Is the API base URL correct? Expected default: http://localhost:1234/v1, Used: {openai_api_base}")
        print("- Check the LM Studio server logs for errors.")

    return {"message": response}



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
