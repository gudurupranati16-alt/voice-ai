"""Translation that understands slang and code-mixing (Hinglish, Tanglish...)."""
import llm


def run(text: str, target: str = "English", glossary: dict = None, **_) -> dict:
    gloss = ""
    if glossary:
        gloss = "Slang glossary (use these meanings):\n" + "\n".join(
            f"- {k} = {v}" for k, v in glossary.items()
        )
    prompt = f"""Translate the message into {target}. The speaker may mix languages or use slang;
translate the intended meaning naturally, not word by word.
{gloss}
Return JSON with keys: "source_language", "translation", "notes" (empty string if none).

Message: {text}"""
    return llm.chat_json(prompt)
