"""Check the server works and measure latency.

1. Start the server:  cd backend && uvicorn main:app --reload
2. In another terminal: python scripts/smoke_test.py [path/to/recording.webm]
Target: total voice round trip under ~3 seconds.
"""
import sys
import time

import httpx

BASE = "http://localhost:8000"


def main():
    print("health:", httpx.get(f"{BASE}/health").json())

    t = time.time()
    r = httpx.post(f"{BASE}/chat", json={"text": "I feel distracted", "session_id": "smoke"}, timeout=30)
    print(f"chat ({time.time() - t:.2f}s):", r.json())

    r = httpx.post(f"{BASE}/module/sentiment", json={"text": "This is the third time my order is late!"}, timeout=30)
    print("sentiment:", r.json())

    r = httpx.post(f"{BASE}/module/translate",
                   json={"text": "bhai scene off hai aaj", "target": "English"}, timeout=30)
    print("translate:", r.json())

    if len(sys.argv) > 1:
        with open(sys.argv[1], "rb") as f:
            r = httpx.post(f"{BASE}/voice", files={"audio": (sys.argv[1], f)},
                           data={"modules": "sentiment"}, timeout=60)
        print("voice:", r.json())


if __name__ == "__main__":
    main()
