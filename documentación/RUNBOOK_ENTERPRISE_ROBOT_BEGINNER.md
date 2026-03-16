# RUNBOOK_ENTERPRISE_ROBOT_BEGINNER
Fecha: 2026-03-10

## Objetivo
Guia paso a paso para levantar el bot EnterpriseRobot en entorno local.

## Requisitos
- Python 3.12 instalado.
- Acceso a Telegram y un bot creado con BotFather.
- Opcional: PostgreSQL y Redis si quieres persistencia y cola.

## 1) Preparar entorno
Abre PowerShell en la carpeta del proyecto:
```powershell
cd c:\Users\1973b\zpa\Projects\manufacturing\robot
```

Crear y activar un entorno virtual:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:
```powershell
pip install -r requirements.txt
```

## 2) Configurar variables de entorno
Crea un archivo `.env` en la raiz del proyecto (si no existe) y agrega:
```
TELEGRAM_BOT_TOKEN=TU_TOKEN_DE_TELEGRAM
WEBHOOK_TOKEN=UN_TOKEN_SECRETO
CHATBOT_API_URL=http://127.0.0.1:8000/api/v1/chat
ENTERPRISE_ENABLED=true
ENTERPRISE_MODERATION_ENABLED=false
ENTERPRISE_OWNER_IDS=123456789
```

Opcional (persistencia y colas):
```
DATABASE_URL=postgresql://user:pass@localhost:5432/robot
REDIS_URL=redis://localhost:6379/0
```

## 3) (Opcional) Migraciones de base de datos
Solo si configuraste Postgres:
```powershell
alembic upgrade head
```

## 4) Levantar el API
En una terminal:
```powershell
uvicorn app.api.entrypoint:app --host 127.0.0.1 --port 8000
```

## 5) Levantar el webhook
En otra terminal:
```powershell
uvicorn app.webhook.entrypoint:app --host 127.0.0.1 --port 9000
```

## 6) (Opcional) Levantar el worker
Si usas cola RQ:
```powershell
python worker.py
```

## 7) Registrar el webhook en Telegram
Con el API y webhook arriba, ejecuta:
```powershell
python set_telegram_webhook.py
```

Si usas otro host o puerto, revisa `set_webhook_prod.py`.

## 8) Probar el bot
En Telegram:
- `/start`
- `/adminhelp`
- `/whoami`
- `/fun`

Para activar moderacion:
```
ENTERPRISE_MODERATION_ENABLED=true
```
Reinicia el webhook y prueba:
- `/blacklist add spam`
- Enviar un mensaje con "spam"

## Problemas comunes
No responde:
- Verifica `TELEGRAM_BOT_TOKEN` y `WEBHOOK_TOKEN`.
- Confirma que el webhook esta activo (`/webhookinfo`).
- Revisa logs del webhook.

Permisos:
- Asegura `ENTERPRISE_OWNER_IDS` con tu user id.
- Usa `/whoami` para confirmar rol.

Persistencia:
- Si usas `no-db`, la configuracion se pierde al reiniciar.

## Detener el bot
En cada terminal presiona `Ctrl+C`.
