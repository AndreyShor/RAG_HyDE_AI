# FastAPI server for LLM
from fastapi import FastAPI # type: ignore
from fastapi import HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore

# Config for FastAPI
from core.config import SettingsAPI

# Model for routs 
from routeModel import ChatRequest
# LLM Functionality for API
from LLM import LLM

# LLM Setings
local_api_base = "http://host.docker.internal:1234/v1"
local_api_key = "lm-studio"
model_name = "gemma-3-1b-it" 

app = FastAPI()

# Initialize Settings, CORS
SettingsAPI(app, corsFlag=True)


# Routs of API, for testing, production should be replaced with separate router

@app.get("/start")
async def root():
    return {"message": "Hello World"}


@app.post("/", )
async def send_llm_request(request: ChatRequest): # type: ignore

    try:
        lastMessage = request.messages[-1].content

        # Initialize LLM
        llm = LLM(
            model_name=model_name,
            local_api_key=local_api_key,
            local_api_base=local_api_base
        )

        # if(llm.has_self_reference(lastMessage)):
        #     print("Response persona")
        #     response = llm.get_repsone_relative_to_person_info_HyDE(lastMessage, "john")
        if(llm.has_physics_prefix(lastMessage)):
            print("response physics")
            lastMessage = lastMessage.removeprefix("phy:").removeprefix("Phy:")
            response = llm.get_repsone_relative_to_person_info_RAG(lastMessage, 'john')
        else:
            print("general response")
            response = llm.get_repsone_relative_to_person_info_RAG(lastMessage, 'john')

        return {"message": response}

    except Exception as e:
        print("🔥 INTERNAL ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/RAG")
async def send_llm_request(request: ChatRequest): # type: ignore
    try:
        lastMessage = request.messages[-1].content

        llm = LLM(
            model_name=model_name,
            local_api_key=local_api_key,
            local_api_base=local_api_base
        )

        print("dome")

        resposne = llm.get_response_as_physics_guru_RAG(lastMessage)
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

        response = llm.get_repsone_relative_to_person_info_HyDE(lastMessage, "john")
        return {"message": response}

    except Exception as e:
        print("🔥 INTERNAL ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))






