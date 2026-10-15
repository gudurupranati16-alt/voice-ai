"""Plug-in modules. Each exposes run(text, **opts) -> dict and is registered here.

Add a new module = new file with run(), then add one line to REGISTRY.
"""
from . import sentiment, summarize, translate

REGISTRY = {
    "sentiment": sentiment.run,
    "translate": translate.run,
    "summarize": summarize.run,
}
