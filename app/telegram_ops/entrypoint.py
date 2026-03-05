"""Telegram OPS - Bot de Telegram para checks E2E."""
import os
import logging
import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters, CommandHandler

from dotenv import load_dotenv

from app.telegram_ops.checks import (
    check_api_health,
    check_webhook_health,
    get_webhook_info,
    run_e2e_check,
    mask_token,
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_IDS = os.getenv("ADMIN_CHAT_IDS", "").split(",")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "mysecretwebhooktoken")

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN not set")
    raise SystemExit(1)

RATE_LIMIT_SECONDS = 30
last_run_times = {}


def is_admin(chat_id: int) -> bool:
    """Verifica si el chat_id es un admin autorizado."""
    if not ADMIN_CHAT_IDS or ADMIN_CHAT_IDS == [""]:
        return True
    return str(chat_id) in ADMIN_CHAT_IDS


async def check_rate_limit(chat_id: int) -> bool:
    """Verifica rate limiting para evitar spam."""
    now = datetime.utcnow().timestamp()
    last_run = last_run_times.get(chat_id, 0)
    if now - last_run < RATE_LIMIT_SECONDS:
        return False
    last_run_times[chat_id] = now
    return True


def format_health_response(api_health: dict, webhook_health: dict) -> str:
    """Formatea respuesta para comando /health."""
    api_status = "✅ OK" if api_health.get("status") == "OK" else "❌ FAIL"
    webhook_status = "✅ OK" if webhook_health.get("status") == "OK" else "❌ FAIL"
    
    msg = "🕐 *Estado de Salud*\n\n"
    msg += f"📡 API: {api_status}\n"
    if api_health.get("status") == "FAIL":
        msg += f"   └─ Error: {api_health.get('error', 'Unknown')}\n"
    msg += f"🪝 Webhook: {webhook_status}\n"
    if webhook_health.get("status") == "FAIL":
        msg += f"   └─ Error: {webhook_health.get('error', 'Unknown')}\n"
    return msg


def format_e2e_response(results: dict) -> str:
    """Formatea respuesta para comando /e2e."""
    msg = "🕐 *E2E Check*\n"
    msg += f"Timestamp: {results.get('timestamp', 'N/A')}\n\n"
    
    checks = results.get("checks", {})
    
    for check_name, check_result in checks.items():
        status = check_result.get("status", "UNKNOWN")
        emoji = "✅" if status == "OK" else "❌"
        msg += f"{emoji} {check_name}: {status}\n"
        if status == "FAIL":
            msg += f"   └─ {check_result.get('error', 'Unknown error')}\n"
    
    overall = results.get("overall", "UNKNOWN")
    overall_emoji = "✅" if overall == "OK" else "❌"
    msg += f"\n{overall_emoji} *Overall: {overall}*"
    
    return msg


def format_webhookinfo_response(info: dict) -> str:
    """Formatea respuesta para comando /webhookinfo."""
    if info.get("status") == "FAIL":
        return f"❌ Error: {info.get('error', 'Unknown')}"
    
    msg = "🪝 *Webhook Info*\n\n"
    msg += f"URL: {info.get('url', 'N/A')}\n"
    msg += f"Pending Updates: {info.get('pending_updates', 0)}\n"
    last_error = info.get("last_error")
    if last_error:
        msg += f"Last Error: {last_error}\n"
    else:
        msg += "Last Error: None ✅\n"
    return msg


async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /health command."""
    if not is_admin(update.effective_chat.id):
        await update.message.reply_text("⛔ No autorizado")
        return
    
    await update.message.reply_text("🔄 Checking...")
    
    api_health = await check_api_health()
    webhook_health = await check_webhook_health()
    
    response = format_health_response(api_health, webhook_health)
    await update.message.reply_text(response, parse_mode="Markdown")


async def e2e_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /e2e command."""
    if not is_admin(update.effective_chat.id):
        await update.message.reply_text("⛔ No autorizado")
        return
    
    if not await check_rate_limit(update.effective_chat.id):
        await update.message.reply_text(f"⏳ Rate limit: espera {RATE_LIMIT_SECONDS}s entre ejecuciones")
        return
    
    await update.message.reply_text("🔄 E2E check iniciado...")
    
    results = await run_e2e_check()
    response = format_e2e_response(results)
    
    await update.message.reply_text(response, parse_mode="Markdown")


async def webhookinfo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /webhookinfo command."""
    if not is_admin(update.effective_chat.id):
        await update.message.reply_text("⛔ No autorizado")
        return
    
    await update.message.reply_text("🔄 Obteniendo info...")
    
    info = await get_webhook_info()
    response = format_webhookinfo_response(info)
    
    await update.message.reply_text(response, parse_mode="Markdown")


async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /logs command."""
    if not is_admin(update.effective_chat.id):
        await update.message.reply_text("⛔ No autorizado")
        return
    
    await update.message.reply_text("📋 Logs: Pendiente implementar sistema de logs")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    await update.message.reply_text(
        "🤖 *Telegram E2E Bot*\n\n"
        "Comandos disponibles:\n"
        "/health - Estado de API y Webhook\n"
        "/e2e - Ejecutar checks E2E\n"
        "/webhookinfo - Info de webhook\n"
        "/logs - Últimos eventos\n\n"
        "Usa /e2e para verificar el sistema.",
        parse_mode="Markdown"
    )


def create_app():
    """Crea la aplicación del bot."""
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("health", health_command))
    app.add_handler(CommandHandler("e2e", e2e_command))
    app.add_handler(CommandHandler("webhookinfo", webhookinfo_command))
    app.add_handler(CommandHandler("logs", logs_command))
    
    logger.info("Telegram OPS Bot inicializado")
    logger.info(f"Admin Chat IDs: {ADMIN_CHAT_IDS}")
    
    return app


app = create_app()


def main():
    """Punto de entrada."""
    logger.info("Starting Telegram OPS Bot...")
    app.run_polling()


if __name__ == "__main__":
    main()
