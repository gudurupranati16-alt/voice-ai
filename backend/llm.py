"""Thin wrappers around Groq: speech-to-text and chat."""
import json

from groq import Groq

import config

client = Groq(api_key=config.GROQ_API_KEY)


def transcribe(audio_bytes: bytes, filename: str = "audio.webm", language=None, hint=None) -> dict:
    """Speech -> text. Returns {"text": ..., "language": ...}."""
    kwargs = dict(
        file=(filename, audio_bytes),
        model=config.STT_MODEL,
        response_format="verbose_json",
    )
    language = language or config.LANGUAGE
    hint = hint or config.STT_HINT
    if language:
        kwargs["language"] = language
    if hint:
        kwargs["prompt"] = hint
    r = client.audio.transcriptions.create(**kwargs)
    return {"text": (r.text or "").strip(), "language": getattr(r, "language", None)}


def chat(messages: list, system: str = None, temperature: float = 0.6, max_tokens: int = 300) -> str:
    """One chat completion. `messages` is a list of {"role", "content"}."""
    full = [{"role": "system", "content": system or config.SYSTEM_PROMPT}] + messages
    r = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=full,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return r.choices[0].message.content.strip()


def chat_stream(messages: list, system: str = None, temperature: float = 0.6, max_tokens: int = 300):
    """Yields text chunks as they arrive (for WebSocket / real-time use)."""
    full = [{"role": "system", "content": system or config.SYSTEM_PROMPT}] + messages
    stream = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=full,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            yield piece


def chat_json(prompt: str, system: str = "You return only valid JSON.", max_tokens: int = 400) -> dict:
    """Ask the LLM for a JSON object and parse it. Used by the plug-in modules."""
    r = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
        max_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    try:
        return json.loads(r.choices[0].message.content)
    except json.JSONDecodeError:
        return {"error": "model did not return valid JSON"}
