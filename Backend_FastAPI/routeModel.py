from pydantic import BaseModel
from typing import List

## This is the model for the main routs 

class Message(BaseModel):
    role: str
    content: str   

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: float