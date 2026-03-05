"""Telegram OPS - Checks functions."""
import httpx
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

API_BASE = os.getenv("API_HOST", "127.0.0.1")
API_PORT = os.getenv("API_PORT", "8000")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT", "8001")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "mysecretwebhooktoken")


def mask_token(token: str) -> str:
    """Enmaskara un token para no exponerlo completo."""
    if len(token) <= 8:
        return "***"
    return f"{token[:4]}...{token[-4:]}"


async def check_api_health() -> Dict[str, Any]:
    """Check API health endpoint."""
    url = f"http://{API_BASE}:{API_PORT}/health"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return {"status": "OK", "code": resp.status_code, "response": resp.json()}
            return {"status": "FAIL", "code": resp.status_code, "error": resp.text}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


async def check_api_chat() -> Dict[str, Any]:
    """Check API chat endpoint."""
    url = f"http://{API_BASE}:{API_PORT}/api/v1/chat"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, params={"message": "test", "session_id": "e2e"})
            if resp.status_code == 200:
                return {"status": "OK", "code": resp.status_code, "response": resp.json()}
            return {"status": "FAIL", "code": resp.status_code, "error": resp.text}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


async def check_webhook_health() -> Dict[str, Any]:
    """Check Webhook health endpoint."""
    url = f"http://{API_BASE}:{WEBHOOK_PORT}/health"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return {"status": "OK", "code": resp.status_code, "response": resp.json()}
            return {"status": "FAIL", "code": resp.status_code, "error": resp.text}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


async def check_webhook_local() -> Dict[str, Any]:
    """Check Webhook local endpoint."""
    # El webhook valida contra TELEGRAM_BOT_TOKEN, no WEBHOOK_TOKEN
    url = f"http://{API_BASE}:{WEBHOOK_PORT}/webhook/{TELEGRAM_TOKEN}"
    payload = {
        "update_id": 999999999,
        "message": {
            "message_id": 1,
            "chat": {"id": 123456789, "type": "private"},
            "text": "/start",
            "date": int(datetime.utcnow().timestamp())
        }
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                return {"status": "OK", "code": resp.status_code}
            return {"status": "FAIL", "code": resp.status_code, "error": resp.text}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


async def get_webhook_info() -> Dict[str, Any]:
    """Get webhook info from Telegram."""
    if not TELEGRAM_TOKEN:
        return {"status": "FAIL", "error": "TELEGRAM_BOT_TOKEN not set"}
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    result = data.get("result", {})
                    masked_url = result.get("url", "").replace(TELEGRAM_TOKEN, mask_token(TELEGRAM_TOKEN))
                    return {
                        "status": "OK",
                        "url": masked_url,
                        "has_custom_url": result.get("has_custom_certificate", False),
                        "pending_updates": result.get("pending_update_count", 0),
                        "last_error": result.get("last_error_message"),
                    }
            return {"status": "FAIL", "code": resp.status_code, "error": resp.text}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


async def check_webhook_public(ngrok_url: str) -> Dict[str, Any]:
    """Check Webhook public endpoint via ngrok."""
    if not ngrok_url:
        return {"status": "FAIL", "error": "ngrok_url not provided"}
    
    url = f"{ngrok_url}/webhook/{TELEGRAM_TOKEN}"
    payload = {
        "update_id": 999999998,
        "message": {
            "message_id": 1,
            "chat": {"id": 123456789, "type": "private"},
            "text": "/start",
            "date": int(datetime.utcnow().timestamp())
        }
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                return {"status": "OK", "code": resp.status_code, "url": url}
            return {"status": "FAIL", "code": resp.status_code, "error": resp.text}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


async def run_e2e_check() -> Dict[str, Any]:
    """Run complete E2E check."""
    results = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "checks": {}
    }
    
    results["checks"]["api_health"] = await check_api_health()
    results["checks"]["api_chat"] = await check_api_chat()
    results["checks"]["webhook_health"] = await check_webhook_health()
    results["checks"]["webhook_local"] = await check_webhook_local()
    results["checks"]["telegram_webhook_info"] = await get_webhook_info()
    
    all_ok = all(
        check.get("status") == "OK" 
        for check in results["checks"].values()
    )
    results["overall"] = "OK" if all_ok else "FAIL"
    
    return results
