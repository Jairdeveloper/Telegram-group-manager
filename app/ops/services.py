"""Application services for chat and operational commands."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Callable, Dict, Iterable, Optional, Sequence, Tuple

from app.api.bootstrap import build_api_runtime
from app.ops.events import get_event_store, record_event

from . import checks as ops_checks


@lru_cache(maxsize=1)
def _get_default_api_runtime():
    """Return a process-wide API runtime for application services."""
    return build_api_runtime()


def handle_chat_message(chat_id: int, text: str, *, agent=None, storage=None) -> Dict[str, Any]:
    """Process a chat message using the chatbot domain service."""
    runtime = None
    if agent is None or storage is None:
        runtime = _get_default_api_runtime()
    agent = agent or runtime.agent
    storage = storage or runtime.storage

    session_id = str(chat_id)
    response = agent.process(text)
    storage.save(session_id, text, response.text)

    return {
        "chat_id": chat_id,
        "session_id": session_id,
        "message": text,
        "response": response.text,
        "confidence": response.confidence,
        "source": response.source,
        "pattern_matched": response.pattern_matched,
    }


def format_health_response(api_health: Dict[str, Any], webhook_health: Dict[str, Any]) -> str:
    """Format response for /health."""
    api_status = "OK" if api_health.get("status") == "OK" else "FAIL"
    webhook_status = "OK" if webhook_health.get("status") == "OK" else "FAIL"

    lines = [
        "Estado de Salud",
        "",
        f"API: {api_status}",
    ]
    if api_health.get("status") == "FAIL":
        lines.append(f"  Error: {api_health.get('error', 'Unknown')}")

    lines.append(f"Webhook: {webhook_status}")
    if webhook_health.get("status") == "FAIL":
        lines.append(f"  Error: {webhook_health.get('error', 'Unknown')}")

    return "\n".join(lines)


def format_e2e_response(results: Dict[str, Any]) -> str:
    """Format response for /e2e in plain text."""
    run_id = results.get("run_id", "N/A")
    lines = [
        f"E2E Check (run_id: {run_id})",
        f"Timestamp: {results.get('timestamp', 'N/A')}",
        "",
    ]

    checks = results.get("checks", {})
    for check_name, check_result in checks.items():
        status = check_result.get("status", "UNKNOWN")
        marker = "OK" if status == "OK" else "FAIL"
        lines.append(f"[{marker}] {check_name}: {status}")
        if status == "FAIL":
            lines.append(f"  Error: {check_result.get('error', 'Unknown error')}")

    lines.extend(["", f"Overall: {results.get('overall', 'UNKNOWN')}"])
    return "\n".join(lines)


def format_webhookinfo_response(info: Dict[str, Any]) -> str:
    """Format response for /webhookinfo."""
    if info.get("status") == "FAIL":
        return f"Error: {info.get('error', 'Unknown')}"

    lines = [
        "Webhook Info",
        "",
        f"URL: {info.get('url', 'N/A')}",
        f"Pending Updates: {info.get('pending_updates', 0)}",
    ]
    last_error = info.get("last_error")
    if last_error:
        lines.append(f"Last Error: {last_error}")
    else:
        lines.append("Last Error: None")
    return "\n".join(lines)


def _parse_logs_args(args: Sequence[str]) -> Tuple[int, Optional[int], Optional[int]]:
    limit = 20
    chat_id = None
    update_id = None

    i = 0
    while i < len(args):
        token = args[i].strip().lower()
        if token.isdigit():
            limit = int(token)
            i += 1
            continue
        if token == "chat" and i + 1 < len(args) and args[i + 1].strip().lstrip("-").isdigit():
            chat_id = int(args[i + 1])
            i += 2
            continue
        if token == "update" and i + 1 < len(args) and args[i + 1].strip().lstrip("-").isdigit():
            update_id = int(args[i + 1])
            i += 2
            continue
        i += 1

    limit = max(1, min(limit, 200))
    return limit, chat_id, update_id


def _format_logs_response(events: Iterable[Dict[str, Any]], *, limit: int, filter_chat_id=None, filter_update_id=None) -> str:
    events = list(events)
    if not events:
        return "Sin eventos recientes (o filtros sin match)."

    lines = []
    for ev in events:
        ts = ev.get("ts_utc", "N/A")
        component = ev.get("component", "?")
        name = ev.get("event", "?")
        level = ev.get("level", "INFO")
        chat_id = ev.get("chat_id")
        update_id = ev.get("update_id")
        job_id = ev.get("job_id")

        suffix_parts = []
        if chat_id is not None:
            suffix_parts.append(f"chat={chat_id}")
        if update_id is not None:
            suffix_parts.append(f"update={update_id}")
        if job_id is not None:
            suffix_parts.append(f"job={job_id}")

        suffix = f" ({', '.join(suffix_parts)})" if suffix_parts else ""
        lines.append(f"{ts} [{level}] {component} {name}{suffix}")

    header = f"Ultimos eventos ({len(events)}/{limit})"
    if filter_chat_id is not None:
        header += f" | chat={filter_chat_id}"
    if filter_update_id is not None:
        header += f" | update={filter_update_id}"

    return header + "\n\n" + "\n".join(lines)


async def execute_e2e_command(
    chat_id: int,
    *,
    rate_limit_check: Optional[Callable[[int], Any]] = None,
    run_id: Optional[str] = None,
    run_e2e_check_fn: Callable[[], Any] = ops_checks.run_e2e_check,
    record_event_fn: Callable[..., None] = record_event,
) -> Dict[str, Any]:
    """Execute /e2e as an application service."""
    if rate_limit_check is not None and not await rate_limit_check(chat_id):
        return {
            "status": "rate_limited",
            "command": "/e2e",
            "response_text": "Rate limit: espera 30s entre ejecuciones",
        }

    run_id = run_id or str(uuid.uuid4())[:8]
    record_event_fn(component="ops", event="ops.e2e.requested", chat_id=chat_id, run_id=run_id)

    try:
        results = await run_e2e_check_fn()
        results["run_id"] = run_id
        response_text = format_e2e_response(results)
        record_event_fn(
            component="ops",
            event="ops.e2e.completed",
            chat_id=chat_id,
            run_id=run_id,
            overall=results.get("overall"),
        )
        return {
            "status": "ok",
            "command": "/e2e",
            "run_id": run_id,
            "response_text": response_text,
            "results": results,
        }
    except Exception as exc:
        record_event_fn(
            component="ops",
            event="ops.e2e.failed",
            level="ERROR",
            chat_id=chat_id,
            run_id=run_id,
            error=str(exc),
        )
        return {
            "status": "failed",
            "command": "/e2e",
            "run_id": run_id,
            "response_text": (
                f"E2E check failed (run_id: {run_id})\n"
                f"Timestamp: {datetime.now(timezone.utc).isoformat()}\n"
                f"Error: {exc}"
            ),
            "error": str(exc),
        }


async def handle_ops_command(
    chat_id: int,
    command: str,
    args: Sequence[str] = (),
    *,
    is_admin_fn: Optional[Callable[[int], bool]] = None,
    rate_limit_check: Optional[Callable[[int], Any]] = None,
    get_event_store_fn: Callable[[], Any] = get_event_store,
    record_event_fn: Callable[..., None] = record_event,
    check_api_health_fn: Callable[[], Any] = ops_checks.check_api_health,
    check_webhook_health_fn: Callable[[], Any] = ops_checks.check_webhook_health,
    get_webhook_info_fn: Callable[[], Any] = ops_checks.get_webhook_info,
    run_e2e_check_fn: Callable[[], Any] = ops_checks.run_e2e_check,
) -> Dict[str, Any]:
    """Handle an OPS command independent from the Telegram transport."""
    normalized_command = (command or "").strip().lower()
    args = tuple(args or ())

    if is_admin_fn is not None and not is_admin_fn(chat_id):
        return {"status": "unauthorized", "command": normalized_command, "response_text": "No autorizado"}

    if normalized_command == "/health":
        api_health = await check_api_health_fn()
        webhook_health = await check_webhook_health_fn()
        return {
            "status": "ok",
            "command": normalized_command,
            "response_text": format_health_response(api_health, webhook_health),
        }

    if normalized_command == "/webhookinfo":
        info = await get_webhook_info_fn()
        return {
            "status": "ok" if info.get("status") == "OK" else "failed",
            "command": normalized_command,
            "response_text": format_webhookinfo_response(info),
            "info": info,
        }

    if normalized_command == "/logs":
        limit, filter_chat_id, filter_update_id = _parse_logs_args(args)
        record_event_fn(
            component="ops",
            event="ops.logs_requested",
            chat_id=chat_id,
            limit=limit,
            filter_chat_id=filter_chat_id,
            filter_update_id=filter_update_id,
        )

        store = get_event_store_fn()
        raw_events = store.tail(min(1000, max(limit * 5, limit)))
        events = []
        for ev in raw_events:
            if filter_chat_id is not None and ev.get("chat_id") != filter_chat_id:
                continue
            if filter_update_id is not None and ev.get("update_id") != filter_update_id:
                continue
            events.append(ev)
            if len(events) >= limit:
                break

        return {
            "status": "ok",
            "command": normalized_command,
            "response_text": _format_logs_response(
                events,
                limit=limit,
                filter_chat_id=filter_chat_id,
                filter_update_id=filter_update_id,
            ),
        }

    if normalized_command == "/e2e":
        return await execute_e2e_command(
            chat_id,
            rate_limit_check=rate_limit_check,
            run_e2e_check_fn=run_e2e_check_fn,
            record_event_fn=record_event_fn,
        )

    return {
        "status": "unsupported",
        "command": normalized_command,
        "response_text": f"Unsupported command: {normalized_command}",
    }
