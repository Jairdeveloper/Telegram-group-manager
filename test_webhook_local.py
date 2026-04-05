"""Script para simular una solicitud Telegram al webhook."""

import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_TOKEN = os.getenv("WEBHOOK_TOKEN", "mysecretwebhooktoken")

# Update de ejemplo de Telegram
sample_update = {
    "update_id": 999999,
    "message": {
        "message_id": 1,
        "date": 1704096000,
        "chat": {
            "id": 12345,
            "type": "private",
            "first_name": "Test"
        },
        "from": {
            "id": 12345,
            "is_bot": False,
            "first_name": "Test"
        },
        "text": "/start"
    }
}

#Configurar el header secret_token como Telegram lo haría
headers = {
    "X-Telegram-Bot-Api-Secret-Token": WEBHOOK_TOKEN,
    "Content-Type": "application/json"
}

# Probar contra el servidor local
print("Enviando mensaje de prueba al webhook local...")
print(f"Endpoint: http://localhost:8001/webhook/{WEBHOOK_TOKEN}")
print(f"Update: {json.dumps(sample_update, indent=2)}")
print()

try:
    response = httpx.post(
        f"http://localhost:8001/webhook/{WEBHOOK_TOKEN}",
        json=sample_update,
        headers=headers,
        timeout=10
    )
    
    print(f"✅ Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code != 200:
        print()
        print(f"❌ Error: El servidor respondió con {response.status_code}")
    else:
        print()
        print("✅ El webhook respondió correctamente")
        
except Exception as e:
    print(f"❌ Error de conexión: {e}")
    print()
    print("Asegúrate de:")
    print("  1. Ejecutar el servidor: uvicorn app.webhook.entrypoint:app --port 8001")
    print("  2. El servidor debe estar escuchando en http://localhost:8001")
