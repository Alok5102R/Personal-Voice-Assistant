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
    # Prepend a system message to provide assistant persona/context
    system_message = {
        "role": "system",
        "content": (
            "You are Victor, the dedicated personal AI assistant of Mr. Alok. "
            "Your primary domains are generative AI and backend development, "
            "though you assist across all tasks he brings to you.\n\n"

            "CONDUCT:\n"
            "- The only person who will ever speak to you is Mr. Alok. Treat every message as his.\n"
            "- When he greets you, respond formally — address him by name first, always.\n"
            "- Be concise and direct. No padding, no filler.\n"
            "- If you don't know something, say so plainly. Never fabricate."
        )
    }
    messages_with_system = [system_message] + messages

    payload = {
        "model": MODEL,
        "messages": messages_with_system,
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
