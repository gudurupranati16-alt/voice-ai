"""Load demo data so the dashboard/RAG never looks empty.

Usage (from voice-kit/): python scripts/seed_demo.py
Edit ITEMS for whatever the hackathon problem statement is.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
import memory  # noqa: E402

ITEMS = [
    {"kind": "goal", "text": "Crack placements by December"},
    {"kind": "reflection", "text": "I got stuck watching reels for 90 minutes at night",
     "meta": {"activity": "Instagram Reels", "emotion": "regret", "duration_min": 90, "hour": 22}},
    {"kind": "reflection", "text": "Lost an hour on YouTube after lunch instead of studying",
     "meta": {"activity": "YouTube", "emotion": "regret", "duration_min": 60, "hour": 14}},
    {"kind": "reflection", "text": "Opened Twitter while studying and scrolled for 45 minutes",
     "meta": {"activity": "X/Twitter", "emotion": "regret", "duration_min": 45, "hour": 16}},
]

if __name__ == "__main__":
    print(f"Seeded {memory.seed(ITEMS)} memories")
