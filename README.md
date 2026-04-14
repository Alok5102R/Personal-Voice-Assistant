# Voice Assistant

Local voice assistant powered by Llama 3.2 3B via Ollama.

## Stack
- **LLM**: Ollama (llama3.2:3b)
- **Backend**: Python + FastAPI (streaming SSE)
- **Frontend**: HTML + Tailwind + Web Speech API (VAD + TTS)

## Setup

### 1. Make sure Ollama is running
```bash
ollama serve
ollama pull llama3.2:3b
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend
Open `frontend/index.html` directly in Chrome/Edge.

> ⚠️ Use Chrome or Edge. Firefox has limited Web Speech API support.
> ⚠️ Must be served from localhost or HTTPS for mic access. If opening as a file:// URL doesn't give mic access, run:
> `python -m http.server 3000` from the `frontend/` folder and go to `http://localhost:3000`

## How it works

1. Click the mic button to start VAD (voice activity detection)
2. Speak — the app detects 1.5s of silence, then sends your speech to the backend
3. Backend streams the LLM response back via SSE
4. Response is read aloud via the browser's TTS engine
5. The orb animates through: idle → listening → thinking → speaking

## Orb states
- **idle**: slow float
- **listening**: expanding rings, pulsing
- **thinking**: color shimmer
- **speaking**: cyan pulse + waveform bars

## Troubleshooting
- **Mic not working**: Make sure you're on `localhost`, not `file://`
- **Ollama offline warning**: Run `ollama serve` and ensure model is pulled
- **No TTS voice**: Browser needs a voice pack installed. Check Settings → Language
