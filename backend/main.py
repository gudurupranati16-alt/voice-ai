"""Voice AI starter kit: FastAPI backend.

Run:  cd backend && uvicorn main:app --reload
Open: http://localhost:8000
"""
import asyncio
import time
from pathlib import Path
from typing import Optional

import httpx
from fastapi import FastAPI, File, Form, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import config
import llm
import memory
from modules import REGISTRY

app = FastAPI(title="Voice AI Kit")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# session_id -> list of {"role", "content"}
SESSIONS: dict = {}


# ---------- helpers ----------
def _history(session_id: str) -> list:
    return SESSIONS.setdefault(session_id, [])


def _build_system(user_text: str, use_memory: bool) -> str:
    """System prompt + (optionally) retrieved memories = the RAG step."""
    system = config.SYSTEM_PROMPT
    if use_memory:
        hits = memory.search(user_text, k=3)
        if hits:
            ctx = "\n".join(f"- ({h['kind']}) {h['text']}" for h in hits)
            system += f"\n\nRelevant things you know about this user:\n{ctx}\nUse them naturally if helpful."
    return system


def _reply(session_id: str, user_text: str, use_memory: bool = True) -> str:
    hist = _history(session_id)
    hist.append({"role": "user", "content": user_text})
    reply = llm.chat(hist[-config.HISTORY_TURNS:], system=_build_system(user_text, use_memory))
    hist.append({"role": "assistant", "content": reply})
    return reply


def _run_modules(text: str, modules: str, target: str) -> dict:
    out = {}
    for name in [m.strip() for m in (modules or "").split(",") if m.strip()]:
        fn = REGISTRY.get(name)
        if fn:
            out[name] = fn(text, target=target)
    return out


# ---------- models ----------
class ChatIn(BaseModel):
    text: str
    session_id: str = "default"
    use_memory: bool = True


class ModuleIn(BaseModel):
    text: str
    target: str = "English"


class MemoryIn(BaseModel):
    kind: str
    text: str
    meta: Optional[dict] = None


class SpeakIn(BaseModel):
    text: str


# ---------- routes ----------
@app.get("/health")
def health():
    return {"ok": True, "groq_key_set": bool(config.GROQ_API_KEY)}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...), language: Optional[str] = Form(None)):
    data = await audio.read()
    return llm.transcribe(data, audio.filename or "audio.webm", language)


@app.post("/chat")
def chat(body: ChatIn):
    t0 = time.time()
    reply = _reply(body.session_id, body.text, body.use_memory)
    return {"reply": reply, "latency_s": round(time.time() - t0, 2)}


@app.post("/voice")
async def voice(
    audio: UploadFile = File(...),
    session_id: str = Form("default"),
    language: Optional[str] = Form(None),
    modules: str = Form(""),          # e.g. "sentiment,translate"
    target: str = Form("English"),    # translation target
):
    """Full loop: audio in -> transcript -> (modules) -> reply text."""
    t0 = time.time()
    data = await audio.read()
    stt = llm.transcribe(data, audio.filename or "audio.webm", language)
    if not stt["text"]:
        raise HTTPException(400, "No speech detected")
    t1 = time.time()
    reply = _reply(session_id, stt["text"])
    t2 = time.time()
    return {
        "transcript": stt["text"],
        "language": stt["language"],
        "reply": reply,
        "modules": _run_modules(stt["text"], modules, target),
        "latency_s": {"stt": round(t1 - t0, 2), "llm": round(t2 - t1, 2), "total": round(time.time() - t0, 2)},
    }


@app.post("/module/{name}")
def run_module(name: str, body: ModuleIn):
    fn = REGISTRY.get(name)
    if not fn:
        raise HTTPException(404, f"Unknown module. Available: {list(REGISTRY)}")
    return fn(body.text, target=body.target)


@app.post("/speak")
async def speak(body: SpeakIn):
    """Optional nicer TTS via ElevenLabs. The frontend falls back to browser TTS on 501."""
    if not config.ELEVENLABS_API_KEY:
        raise HTTPException(501, "ELEVENLABS_API_KEY not set; use browser speech synthesis")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}"
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.post(
            url,
            headers={"xi-api-key": config.ELEVENLABS_API_KEY},
            json={"text": body.text, "model_id": "eleven_multilingual_v2"},
        )
    if r.status_code != 200:
        raise HTTPException(502, "TTS provider error")
    return Response(content=r.content, media_type="audio/mpeg")


@app.post("/memory")
def add_memory(body: MemoryIn):
    return {"id": memory.add(body.kind, body.text, body.meta)}


@app.get("/memory")
def list_memory(kind: Optional[str] = None, n: int = 20):
    return memory.recent(kind, n)


@app.post("/session/{session_id}/reset")
def reset(session_id: str):
    SESSIONS.pop(session_id, None)
    return {"ok": True}


@app.websocket("/ws")
async def ws_chat(ws: WebSocket):
    """Real-time streaming. Client sends {"text": "..."}; server streams {"token": "..."} then {"done": true}."""
    await ws.accept()
    hist = []
    try:
        while True:
            msg = await ws.receive_json()
            text = msg.get("text", "")
            hist.append({"role": "user", "content": text})
            full = ""
            gen = llm.chat_stream(hist[-config.HISTORY_TURNS:], system=_build_system(text, True))
            loop = asyncio.get_running_loop()
            while True:
                piece = await loop.run_in_executor(None, next, gen, None)
                if piece is None:
                    break
                full += piece
                await ws.send_json({"token": piece})
            hist.append({"role": "assistant", "content": full})
            await ws.send_json({"done": True})
    except WebSocketDisconnect:
        pass


# Serve the frontend from the same origin (mic access needs localhost or https)
FRONTEND = Path(__file__).parent.parent / "frontend"
if FRONTEND.exists():
    app.mount("/", StaticFiles(directory=FRONTEND, html=True), name="frontend")
