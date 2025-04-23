from fastapi import FastAPI # type: ignore
from fastapi import HTTPException

from fastapi.middleware.cors import CORSMiddleware

from LLM import LLM
from model import ChatRequest

# LLM Setings
local_api_base = "http://host.docker.internal:1234/v1"
local_api_key = "lm-studio"
model_name = "gemma-3-1b-it" 

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


@app.get("/start")
async def root():
    return {"message": "Hello World"}


@app.post("/", )
async def send_llm_request(request: ChatRequest):
    lastMessage = request.messages[-1].content

    # Initialize LLM
    llm = LLM(
        model_name=model_name,
        local_api_key=local_api_key,
        local_api_base=local_api_base
    )

    llm_response: str = llm.get_response_normal(lastMessage)

    return {"message": llm_response}

@app.post("/RAG")
async def send_llm_request(request: ChatRequest):
    try:
        lastMessage = request.messages[-1].content

        llm = LLM(
            model_name=model_name,
            local_api_key=local_api_key,
            local_api_base=local_api_base
        )

        print("dome")

        resposne = llm.get_response_as_physics_guru(lastMessage)
        return {"message": resposne}

    except Exception as e:
        print("🔥 INTERNAL ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/person")
async def send_llm_request(request: ChatRequest):
    try:
        lastMessage = request.messages[-1].content

        llm = LLM(
            model_name=model_name,
            local_api_key=local_api_key,
            local_api_base=local_api_base
        )

        print("dome")

        response = llm.get_repsone_relative_to_person_info(lastMessage, "john")
        return {"message": response}

    except Exception as e:
        print("🔥 INTERNAL ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))






