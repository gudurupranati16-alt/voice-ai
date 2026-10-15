"""Summary + action items for calls, meetings, lectures, long audio transcripts."""
import llm


def run(text: str, **_) -> dict:
    prompt = f"""Summarize this transcript. Return JSON with keys:
"summary": 2-3 sentences,
"action_items": list of short strings (empty list if none),
"key_topics": list of up to 5 short strings.

Transcript: {text}"""
    return llm.chat_json(prompt, max_tokens=600)
