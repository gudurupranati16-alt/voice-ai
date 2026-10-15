"""Customer-care style sentiment + escalation detection."""
import llm


def run(text: str, **_) -> dict:
    prompt = f"""Analyze this spoken message. Return JSON with keys:
"sentiment": "positive" | "neutral" | "negative",
"emotion": one word (e.g. angry, frustrated, anxious, happy, calm, sad, bored),
"score": number from -1.0 (very negative) to 1.0 (very positive),
"escalate": true if a human should step in (anger, distress, threats, emergency),
"reason": one short sentence.

Message: {text}"""
    return llm.chat_json(prompt)
