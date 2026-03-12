"""Script para configurar el webhook de Telegram."""

import os
import sys
import httpx
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "mysecretwebhooktoken")
WEBHOOK_PORT = os.getenv("WEBHOOK_PORT", "9000")

# URL base de la API de Telegram
TELEGRAM_API = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def get_webhook_info():
    """Obtener información del webhook actual."""
    url = f"{TELEGRAM_API}/getWebhookInfo"
    response = httpx.get(url)
    return response.json()


def set_webhook(webhook_url: str):
    """Configurar el webhook."""
    url = f"{TELEGRAM_API}/setWebhook"
    payload = {
        "url": webhook_url,
        "secret_token": WEBHOOK_TOKEN,
    }
    response = httpx.post(url, json=payload)
    return response.json()


def delete_webhook():
    """Eliminar el webhook."""
    url = f"{TELEGRAM_API}/deleteWebhook"
    response = httpx.post(url)
    return response.json()


def main():
    print("=" * 50)
    print("Configuración de Webhook - ManagerBot")
    print("=" * 50)
    print()

    # Verificar token
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN no está configurado")
        print("Configúralo en el archivo .env")
        sys.exit(1)

    print(f"Bot Token: {TELEGRAM_BOT_TOKEN[:15]}...")
    print(f"Webhook Token: {WEBHOOK_TOKEN}")
    print()

    # Mostrar estado actual
    print("Estado actual del webhook:")
    info = get_webhook_info()
    if info.get("ok"):
        result = info.get("result", {})
        print(f"  URL: {result.get('url', 'No configurado')}")
        print(f"  Pending updates: {result.get('pending_update_count', 0)}")
        print(f"  Last error: {result.get('last_error_message', 'Ninguno')}")
    print()

    # Solicitar URL al usuario
    print("Para configurar el webhook, necesitas una URL pública:")
    print()
    print("OPCIONES:")
    print("1. Desarrollo local (usando ngrok): ngrok http 9000")
    print("2. Producción: https://tu-dominio.com")
    print()
    
    webhook_url = input("Ingresa la URL pública del webhook (incluye /webhook/TOKEN): ").strip()
    
    if not webhook_url:
        print("ERROR: Debes ingresar una URL")
        sys.exit(1)
    
    # Asegurar que la URL termine con el token
    if not webhook_url.endswith(f"/webhook/{WEBHOOK_TOKEN}"):
        webhook_url = f"{webhook_url.rstrip('/')}/webhook/{WEBHOOK_TOKEN}"
    
    print()
    print(f"Configurando webhook: {webhook_url}")
    result = set_webhook(webhook_url)
    
    if result.get("ok"):
        print("✅ Webhook configurado correctamente!")
        print(f"   Description: {result.get('result', {}).get('description', '')}")
    else:
        print(f"❌ Error al configurar webhook: {result.get('description', '')}")
    
    print()
    
    # Verificar estado final
    print("Estado final:")
    info = get_webhook_info()
    if info.get("ok"):
        result = info.get("result", {})
        print(f"  URL: {result.get('url', 'No configurado')}")
        print(f"  Pending updates: {result.get('pending_update_count', 0)}")


if __name__ == "__main__":
    main()
