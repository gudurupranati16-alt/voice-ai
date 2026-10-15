"""Tiny memory store (SQLite) with keyword retrieval.

No extra dependencies, works instantly. If a problem needs real semantic RAG,
swap `search()` for Chroma/FAISS embeddings; keep the same function signatures
so nothing else changes.
"""
import json
import re
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).parent / "memory.db"


def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute(
        """CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            text TEXT NOT NULL,
            meta TEXT DEFAULT '{}',
            created_at REAL NOT NULL
        )"""
    )
    return c


def add(kind: str, text: str, meta: dict = None) -> int:
    with _conn() as c:
        cur = c.execute(
            "INSERT INTO memories (kind, text, meta, created_at) VALUES (?, ?, ?, ?)",
            (kind, text, json.dumps(meta or {}), time.time()),
        )
        return cur.lastrowid


def recent(kind: str = None, n: int = 10) -> list:
    with _conn() as c:
        if kind:
            rows = c.execute(
                "SELECT * FROM memories WHERE kind=? ORDER BY id DESC LIMIT ?", (kind, n)
            ).fetchall()
        else:
            rows = c.execute("SELECT * FROM memories ORDER BY id DESC LIMIT ?", (n,)).fetchall()
    return [dict(r) for r in rows]


def _tokens(s: str) -> set:
    return set(re.findall(r"\w+", s.lower()))


def search(query: str, k: int = 3, kind: str = None) -> list:
    """Return the k memories sharing the most words with the query."""
    q = _tokens(query)
    pool = recent(kind, n=500)
    scored = []
    for m in pool:
        overlap = len(q & _tokens(m["text"]))
        if overlap:
            scored.append((overlap, m))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [m for _, m in scored[:k]]


def seed(items: list) -> int:
    """items: [{"kind": "...", "text": "...", "meta": {...}}]. Use for demo data."""
    for it in items:
        add(it["kind"], it["text"], it.get("meta"))
    return len(items)
