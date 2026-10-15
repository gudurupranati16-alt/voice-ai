# Voice AI Starter Kit

Speak → transcript → LLM (with memory/RAG) → spoken reply. Plus plug-in modules
(sentiment, translation, summary) and a WebSocket for real-time streaming.

## Run it (5 minutes)

```bash
cd voice-kit
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # paste your GROQ_API_KEY
python scripts/seed_demo.py # optional demo memories
cd backend && uvicorn main:app --reload
```

Open http://localhost:8000, tap the mic, speak. (Mic access needs `localhost` or https.)

Check latency: `python scripts/smoke_test.py` (target: total round trip under ~3 s).

## Layout

```
backend/
  config.py     <- EDIT FIRST: SYSTEM_PROMPT, language, models, STT hint words
  llm.py        Groq wrappers: transcribe, chat, chat_stream, chat_json
  memory.py     SQLite memory + keyword retrieval (swap for Chroma if needed)
  main.py       API: /voice /chat /transcribe /speak /module/{name} /memory /ws
  modules/      sentiment, translate, summarize  (register new ones in __init__.py)
frontend/index.html   mic UI, chat bubbles, sentiment/translate toggles
scripts/              seed_demo.py, smoke_test.py
```

## Reskin for a new problem statement (the hackathon-day routine)

1. **config.py → `SYSTEM_PROMPT`**: who the assistant is, tone, length, language rules.
2. **Memory/RAG**: edit `scripts/seed_demo.py` with goals/FAQs/knowledge, run it. Anything
   added with `memory.add(kind, text, meta)` is retrieved automatically in `/voice` and `/chat`.
3. **Pick modules** in the UI toggles or pass `modules=sentiment,translate` to `/voice`.
4. **New module?** Create `modules/yours.py` with `run(text, **opts) -> dict`, add one line to
   `REGISTRY`. It is then available at `POST /module/yours`.
5. **Accents/slang/code-mixing**: put domain words in `STT_HINT`, and pass a `glossary`
   dict to the translate module (e.g. `{"scene off hai": "the situation is bad"}`).
6. **Real-time**: connect to `ws://localhost:8000/ws`, send `{"text": "..."}`, receive
   `{"token": "..."}` chunks then `{"done": true}`.

## Not included (add if the problem needs it)

| Need | Add |
|---|---|
| Background noise | `noisereduce` or DeepFilterNet before `transcribe`; Silero VAD to skip silence |
| Audio file upload | `/transcribe` already accepts files; add chunking for files over 25 MB |
| Speaker separation | `pyannote.audio` |
| Camera attention | MediaPipe Face Mesh in the browser (eye-closure, head pose) |
| Semantic RAG | Chroma + embeddings behind `memory.search()` |
| Better Indian-language ASR | AI4Bharat IndicConformer / IndicWhisper |

## Fallbacks for demo day

- No Wi-Fi: hotspot; keep a pre-recorded demo video.
- ElevenLabs down or no key: the UI automatically falls back to the browser voice.
- Mic fails: type in the text box; the flow is the same.
