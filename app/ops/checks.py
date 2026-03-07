"""Reusable operational checks shared across Telegram transports."""

import logging
import os
import time
from itertools import count
from datetime import datetime, timezone
from typing import Any, Dict

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

API_BASE = os.getenv("API_HOST", "127.0.0.1")
API_PORT = os.getenv("API_PORT", "8000")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT", "8001")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NGROK_URL = os.getenv("NGROK_URL") or os.getenv("NGROK_HTTPS_URL")
_PROBE_UPDATE_IDS = count(start=time.time_ns())


def mask_token(token: str) -> str:
    """Mask a token before exposing it in diagnostics."""
    if len(token) <= 8:
        return "***"
    return f"{token[:4]}...{token[-4:]}"


def add_hint(check_result: Dict[str, Any], error_type: str) -> Dict[str, Any]:
    """Add actionable hint to a failed check result."""
    if check_result.get("status") == "OK":
        return check_result

    hints = {
        "connection_refused": "Verifica que el servicio esté corriendo en el puerto correcto",
        "api_health": "Ejecuta: uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000",
        "api_chat": "Verifica que la API esté corriendo y el brain esté configurado",
        "webhook_health": "Ejecuta: uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 8001",
        "webhook_local": "Verifica que el webhook esté corriendo y el token sea correcto",
        "webhook_public": "Ejecuta: ngrok http 8001 y luego setWebhook",
        "telegram_webhook_info": "Ejecuta: python set_webhook_prod.py set <URL>",
        "timeout": "El servicio no responde - verifica que esté corriendo",
        "403": "Token inválido - verifica TELEGRAM_BOT_TOKEN en .env",
        "404": "Ruta no encontrada - verifica la URL del webhook",
        "500": "Error interno del servidor - revisa los logs",
    }

    check_result = dict(check_result)
    check_result["hint"] = hints.get(error_type, "Revisa los logs para más detalles")
    return check_result


def build_probe_update(*, text: str = "/start") -> Dict[str, Any]:
    """Build a synthetic Telegram update with a unique update_id."""
    now = datetime.now(timezone.utc)
    return {
        "update_id": next(_PROBE_UPDATE_IDS),
        "message": {
            "message_id": 1,
            "chat": {"id": 123456789, "type": "private"},
            "text": text,
            "date": int(now.timestamp()),
        },
    }


async def check_api_health() -> Dict[str, Any]:
    """Check API health endpoint."""
    url = f"http://{API_BASE}:{API_PORT}/health"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return {"status": "OK", "code": resp.status_code, "response": resp.json()}
            return add_hint({"status": "FAIL", "code": resp.status_code, "error": resp.text}, "api_health")
    except httpx.ConnectError:
        return add_hint({"status": "FAIL", "error": "Connection refused"}, "connection_refused")
    except httpx.TimeoutException:
        return add_hint({"status": "FAIL", "error": "Timeout"}, "timeout")
    except Exception as exc:
        return add_hint({"status": "FAIL", "error": str(exc)}, "api_health")


async def check_api_chat() -> Dict[str, Any]:
    """Check API chat endpoint."""
    url = f"http://{API_BASE}:{API_PORT}/api/v1/chat"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, params={"message": "test", "session_id": "e2e"})
            if resp.status_code == 200:
                return {"status": "OK", "code": resp.status_code, "response": resp.json()}
            return add_hint({"status": "FAIL", "code": resp.status_code, "error": resp.text}, "api_chat")
    except httpx.ConnectError:
        return add_hint({"status": "FAIL", "error": "Connection refused"}, "connection_refused")
    except httpx.TimeoutException:
        return add_hint({"status": "FAIL", "error": "Timeout"}, "timeout")
    except Exception as exc:
        return add_hint({"status": "FAIL", "error": str(exc)}, "api_chat")


async def check_webhook_health() -> Dict[str, Any]:
    """Check webhook health endpoint."""
    url = f"http://{API_BASE}:{WEBHOOK_PORT}/health"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                return {"status": "OK", "code": resp.status_code, "response": resp.json()}
            return add_hint({"status": "FAIL", "code": resp.status_code, "error": resp.text}, "webhook_health")
    except httpx.ConnectError:
        return add_hint({"status": "FAIL", "error": "Connection refused"}, "connection_refused")
    except httpx.TimeoutException:
        return add_hint({"status": "FAIL", "error": "Timeout"}, "timeout")
    except Exception as exc:
        return add_hint({"status": "FAIL", "error": str(exc)}, "webhook_health")


async def check_webhook_local() -> Dict[str, Any]:
    """Check webhook local endpoint."""
    url = f"http://{API_BASE}:{WEBHOOK_PORT}/webhook/{TELEGRAM_TOKEN}"
    payload = build_probe_update()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                return {"status": "OK", "code": resp.status_code}
            if resp.status_code == 403:
                return add_hint({"status": "FAIL", "code": resp.status_code, "error": "Invalid token"}, "403")
            if resp.status_code == 404:
                return add_hint({"status": "FAIL", "code": resp.status_code, "error": "Not found"}, "404")
            return add_hint({"status": "FAIL", "code": resp.status_code, "error": resp.text}, "webhook_local")
    except httpx.ConnectError:
        return add_hint({"status": "FAIL", "error": "Connection refused"}, "connection_refused")
    except httpx.TimeoutException:
        return add_hint({"status": "FAIL", "error": "Timeout"}, "timeout")
    except Exception as exc:
        return add_hint({"status": "FAIL", "error": str(exc)}, "webhook_local")


async def get_webhook_info() -> Dict[str, Any]:
    """Get webhook info from Telegram."""
    if not TELEGRAM_TOKEN:
        return add_hint({"status": "FAIL", "error": "TELEGRAM_BOT_TOKEN not set"}, "telegram_webhook_info")

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getWebhookInfo"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("ok"):
                    result = data.get("result", {})
                    masked_url = result.get("url", "").replace(TELEGRAM_TOKEN, mask_token(TELEGRAM_TOKEN))
                    
                    # Check if webhook URL is empty
                    if not result.get("url"):
                        return {
                            "status": "OK",
                            "url": "(no configured)",
                            "has_custom_url": result.get("has_custom_certificate", False),
                            "pending_updates": result.get("pending_update_count", 0),
                            "last_error": result.get("last_error_message"),
                            "hint": "Webhook no configurado. Ejecuta: python set_webhook_prod.py set <URL>",
                        }
                    
                    # Check for errors
                    if result.get("last_error_message"):
                        return add_hint({
                            "status": "OK",
                            "url": masked_url,
                            "has_custom_url": result.get("has_custom_certificate", False),
                            "pending_updates": result.get("pending_update_count", 0),
                            "last_error": result.get("last_error_message"),
                        }, "telegram_webhook_info")
                    
                    return {
                        "status": "OK",
                        "url": masked_url,
                        "has_custom_url": result.get("has_custom_certificate", False),
                        "pending_updates": result.get("pending_update_count", 0),
                        "last_error": result.get("last_error_message"),
                    }
            return add_hint({"status": "FAIL", "code": resp.status_code, "error": resp.text}, "telegram_webhook_info")
    except httpx.ConnectError:
        return add_hint({"status": "FAIL", "error": "Connection refused"}, "connection_refused")
    except httpx.TimeoutException:
        return add_hint({"status": "FAIL", "error": "Timeout"}, "timeout")
    except Exception as exc:
        return add_hint({"status": "FAIL", "error": str(exc)}, "telegram_webhook_info")


async def check_webhook_public(ngrok_url: str) -> Dict[str, Any]:
    """Check webhook public endpoint via ngrok."""
    if not ngrok_url:
        return add_hint({"status": "FAIL", "error": "NGROK_URL not provided"}, "webhook_public")

    url = f"{ngrok_url}/webhook/{TELEGRAM_TOKEN}"
    payload = build_probe_update()
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                return {"status": "OK", "code": resp.status_code, "url": url}
            if resp.status_code == 403:
                return add_hint({"status": "FAIL", "code": resp.status_code, "error": "Invalid token"}, "403")
            if resp.status_code == 404:
                return add_hint({"status": "FAIL", "code": resp.status_code, "error": "Not found - webhook no configurado"}, "404")
            if resp.status_code == 500:
                return add_hint({"status": "FAIL", "code": resp.status_code, "error": "Internal server error"}, "500")
            return add_hint({"status": "FAIL", "code": resp.status_code, "error": resp.text}, "webhook_public")
    except httpx.ConnectError:
        return add_hint({"status": "FAIL", "error": "Connection refused - ngrok no está corriendo"}, "webhook_public")
    except httpx.TimeoutException:
        return add_hint({"status": "FAIL", "error": "Timeout - ngrok no responde"}, "timeout")
    except Exception as exc:
        return add_hint({"status": "FAIL", "error": str(exc)}, "webhook_public")


async def run_e2e_check() -> Dict[str, Any]:
    """Run complete E2E check."""
    results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": {},
    }

    results["checks"]["api_health"] = await check_api_health()
    results["checks"]["api_chat"] = await check_api_chat()
    results["checks"]["webhook_health"] = await check_webhook_health()
    results["checks"]["webhook_local"] = await check_webhook_local()
    results["checks"]["telegram_webhook_info"] = await get_webhook_info()

    # Optional: check public webhook if NGROK_URL is configured
    if NGROK_URL:
        results["checks"]["webhook_public"] = await check_webhook_public(NGROK_URL)

    all_ok = all(check.get("status") == "OK" for check in results["checks"].values())
    results["overall"] = "OK" if all_ok else "FAIL"

    return results
