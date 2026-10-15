"""Single place to reskin the kit for a new problem statement.

On hackathon day, usually you only edit SYSTEM_PROMPT, LANGUAGE and the
modules you plug in from main.py.
"""
import os

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

STT_MODEL = "whisper-large-v3"          # or "whisper-large-v3-turbo" for speed
LLM_MODEL = "llama-3.3-70b-versatile"   # or "llama-3.1-8b-instant" for speed

# None = auto-detect. Or force a code: "en", "hi", "te", "ta" ...
LANGUAGE = None

# Words/slang to bias the speech recognizer (names, domain terms, Hinglish...)
STT_HINT = ""

# ---- EDIT THIS FIRST when the problem statement drops ----
SYSTEM_PROMPT = """You are a friendly voice assistant.
Rules:
- Reply in at most 2 short spoken sentences. No lists, no markdown, no emojis.
- Be warm and natural. Never scold or lecture.
- End with a short question when it helps the conversation move forward.
- Reply in the same language the user spoke.
"""

# How many past messages to send to the LLM each turn
HISTORY_TURNS = 8
