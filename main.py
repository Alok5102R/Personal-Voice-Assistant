import httpx
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: list[Message]

async def stream_ollama(messages: list[dict]):
    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": 0.7,
            "num_predict": 300,
        }
    }
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream("POST", OLLAMA_URL, json=payload) as response:
            async for line in response.aiter_lines():
                if line:
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            chunk = data["message"]["content"]
                            if chunk:
                                yield f"data: {json.dumps({'text': chunk})}\n\n"
                        if data.get("done"):
                            yield f"data: {json.dumps({'done': True})}\n\n"
                    except json.JSONDecodeError:
                        continue

@app.post("/chat")
async def chat(request: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in request.messages]
    return StreamingResponse(
        stream_ollama(messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

@app.get("/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get("http://localhost:11434/api/tags")
            return {"status": "ok", "ollama": r.status_code == 200}
    except Exception:
        return {"status": "ok", "ollama": False}
