"""Script para verificar el estado del webhook."""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN no está configurado")
    exit(1)

api = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"

print("Verificando el estado del webhook en Telegram...")
print(f"Bot: {BOT_TOKEN[:20]}...")
print()

try:
    response = httpx.get(api, timeout=10)
    result = response.json()
    
    if result.get("ok"):
        info = result.get("result", {})
        print("✅ Webhook Info:")
        print(f"   URL: {info.get('url', 'NO CONFIGURADO')}")
        print(f"   Has custom certificate: {info.get('has_custom_certificate', False)}")
        print(f"   Pending update count: {info.get('pending_update_count', 0)}")
        print(f"   IP address: {info.get('ip_address', 'N/A')}")
        print(f"   Last error date: {info.get('last_error_date', 'N/A')}")
        print(f"   Last error message: {info.get('last_error_message', 'N/A')}")
        print(f"   Last synchronization error date: {info.get('last_synchronization_error_date', 'N/A')}")
        
        if info.get('url'):
            print()
            print("🔗 El webhook ESTÁ configurado en Telegram")
            print(f"   Url: {info.get('url')}")
        else:
            print()
            print("❌ El webhook NO está configurado en Telegram")
            print("   El bot NO recibirá mensajes hasta que levantes el webhook")
            
    else:
        print(f"❌ Error: {result.get('description', 'Unknown error')}")
        
except Exception as e:
    print(f"❌ Error de conexión: {e}")
