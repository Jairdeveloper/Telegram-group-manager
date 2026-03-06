"""Transitional Telegram OPS bot for health, webhook and E2E checks.

Operational status:
- Transitional runtime during architecture migration.
- Do not run in parallel with `app.webhook.entrypoint:app` for the same
  `TELEGRAM_BOT_TOKEN`.
- The target architecture moves OPS command dispatch behind the canonical
  webhook ingress instead of a separate polling process.
"""

import logging
import os
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from telegram import Update
from telegram.error import Conflict, NetworkError
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from app.ops.events import get_event_store, record_event
from app.ops.services import (
    execute_e2e_command,
    format_e2e_response,
    handle_ops_command,
)
from app.telegram_ops.checks import (
    check_api_health,
    check_webhook_health,
    get_webhook_info,
    run_e2e_check,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_IDS = os.getenv("ADMIN_CHAT_IDS", "").split(",")

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set")
    raise SystemExit(1)

RATE_LIMIT_SECONDS = 30
last_run_times = {}
LOCK_PATH = os.path.join("logs", "telegram_ops.pid")


def _pid_is_running(pid: int) -> bool:
    """Best-effort process existence check for a stored PID."""
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def acquire_polling_lock() -> int:
    """Prevent multiple local polling instances from starting silently."""
    os.makedirs(os.path.dirname(LOCK_PATH) or ".", exist_ok=True)
    current_pid = os.getpid()

    if os.path.exists(LOCK_PATH):
        try:
            with open(LOCK_PATH, "r", encoding="utf-8") as f:
                existing_pid = int((f.read() or "0").strip())
        except (OSError, ValueError):
            existing_pid = 0

        if existing_pid and existing_pid != current_pid and _pid_is_running(existing_pid):
            raise SystemExit(
                f"Telegram OPS Bot already running with PID {existing_pid}. "
                "Stop the previous instance before starting a new polling process."
            )

    with open(LOCK_PATH, "w", encoding="utf-8") as f:
        f.write(str(current_pid))
    return current_pid


def release_polling_lock(expected_pid: int) -> None:
    """Remove the lock only if it still belongs to this process."""
    try:
        with open(LOCK_PATH, "r", encoding="utf-8") as f:
            stored_pid = int((f.read() or "0").strip())
    except (OSError, ValueError):
        return

    if stored_pid != expected_pid:
        return

    try:
        os.remove(LOCK_PATH)
    except OSError:
        return


def is_admin(chat_id: int) -> bool:
    """Return whether the chat_id is authorized."""
    if not ADMIN_CHAT_IDS or ADMIN_CHAT_IDS == [""]:
        return True
    return str(chat_id) in ADMIN_CHAT_IDS


async def check_rate_limit(chat_id: int) -> bool:
    """Enforce a small per-chat cooldown."""
    now = datetime.now(timezone.utc).timestamp()
    last_run = last_run_times.get(chat_id, 0)
    if now - last_run < RATE_LIMIT_SECONDS:
        return False
    last_run_times[chat_id] = now
    return True


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /health command."""
    if not is_admin(update.effective_chat.id):
        await update.message.reply_text("No autorizado")
        return

    await update.message.reply_text("Checking...")
    result = await handle_ops_command(
        update.effective_chat.id,
        "/health",
        is_admin_fn=is_admin,
        record_event_fn=record_event,
        check_api_health_fn=check_api_health,
        check_webhook_health_fn=check_webhook_health,
    )
    await update.message.reply_text(result["response_text"])


async def e2e_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /e2e command."""
    chat_id = update.effective_chat.id
    if not is_admin(chat_id):
        await update.message.reply_text("No autorizado")
        return

    if not await check_rate_limit(chat_id):
        await update.message.reply_text(f"Rate limit: espera {RATE_LIMIT_SECONDS}s entre ejecuciones")
        return

    run_id = str(uuid.uuid4())[:8]
    ack_msg = await update.message.reply_text(f"E2E check iniciado... (run_id: {run_id})")
    result = await execute_e2e_command(
        chat_id,
        run_id=run_id,
        run_e2e_check_fn=run_e2e_check,
        record_event_fn=record_event,
    )
    await ack_msg.edit_text(result["response_text"])


async def webhookinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /webhookinfo command."""
    if not is_admin(update.effective_chat.id):
        await update.message.reply_text("No autorizado")
        return

    await update.message.reply_text("Obteniendo info...")
    result = await handle_ops_command(
        update.effective_chat.id,
        "/webhookinfo",
        is_admin_fn=is_admin,
        record_event_fn=record_event,
        get_webhook_info_fn=get_webhook_info,
    )
    await update.message.reply_text(result["response_text"])


async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logs command."""
    args = getattr(context, "args", None) or []
    result = await handle_ops_command(
        update.effective_chat.id,
        "/logs",
        args,
        is_admin_fn=is_admin,
        get_event_store_fn=get_event_store,
        record_event_fn=record_event,
    )
    await update.message.reply_text(result["response_text"])


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "Telegram E2E Bot\n\n"
        "Comandos disponibles:\n"
        "/health - Estado de API y Webhook\n"
        "/e2e - Ejecutar checks E2E\n"
        "/webhookinfo - Info de webhook\n"
        "/logs - Ultimos eventos\n\n"
        "Usa /e2e para verificar el sistema."
    )


def create_app():
    """Create the bot application."""
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("health", health_command))
    app.add_handler(CommandHandler("e2e", e2e_command))
    app.add_handler(CommandHandler("webhookinfo", webhookinfo_command))
    app.add_handler(CommandHandler("logs", logs_command))

    logger.info("Telegram OPS Bot inicializado")
    logger.info("Admin Chat IDs: %s", ADMIN_CHAT_IDS)

    return app


app = create_app()


def main():
    """Process entrypoint."""
    lock_pid = acquire_polling_lock()
    logger.info("Starting Telegram OPS Bot...")
    try:
        app.run_polling(drop_pending_updates=True)
    except Conflict:
        logger.error(
            "Telegram polling conflict detected. Another bot instance is using getUpdates."
        )
        raise SystemExit(2)
    except NetworkError as exc:
        logger.error(
            "Telegram network bootstrap failed. Verify outbound connectivity to api.telegram.org: %s",
            exc,
        )
        raise SystemExit(3)
    finally:
        release_polling_lock(lock_pid)


if __name__ == "__main__":
    main()
