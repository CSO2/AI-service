from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Any
from logic import generate_build_suggestion, generate_chat_response
import uvicorn

app = FastAPI(title="AI Service", description="Service for AI features like Builder Bot and Chat", version="1.0.0")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class BuilderBotRequest(BaseModel):
    query: str

class BuildSuggestion(BaseModel):
    components: List[Any]
    totalPrice: float

class BuilderBotResponse(BaseModel):
    message: str
    buildSuggestion: BuildSuggestion

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response_text = generate_chat_response(request.message)
    return ChatResponse(response=response_text)

@app.post("/builder-bot", response_model=BuilderBotResponse)
def builder_bot(request: BuilderBotRequest):
    result = generate_build_suggestion(request.query)
    return BuilderBotResponse(**result)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8089, reload=True)
