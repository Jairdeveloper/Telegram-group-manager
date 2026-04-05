"""Test ultra-simple del webhook."""
import httpx
import json

data = {"update_id": 999, "message": {"chat": {"id": 123}, "text": "/start"}}

try:
    r = httpx.post("http://localhost:8001/webhook/mysecretwebhooktoken", json=data, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Body: {r.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
