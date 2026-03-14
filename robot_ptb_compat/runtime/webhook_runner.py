"""Webhook Runner para la aplicación."""

import asyncio
from typing import Any, Callable, Dict, List, Optional

try:
    from telegram import Bot
    from telegram.request import RequestParameter
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    Bot = None


class WebhookRunner:
    """Runner para ejecutar la aplicación con webhook."""

    def __init__(
        self,
        application: Any,
        bot: Optional[Any] = None,
    ):
        """Inicializa el runner.

        Args:
            application: Aplicación PTB
            bot: Bot de Telegram (opcional)
        """
        self._application = application
        self._bot = bot
        self._webhook_info: Dict[str, Any] = {}
        self._running = False

    @property
    def bot(self) -> Optional[Any]:
        """Obtiene el bot."""
        return self._bot

    @property
    def webhook_info(self) -> Dict[str, Any]:
        """Obtiene información del webhook."""
        return self._webhook_info

    @property
    def is_running(self) -> bool:
        """Retorna si el runner está ejecutándose."""
        return self._running

    async def start(
        self,
        listen: str = "0.0.0.0",
        port: int = 8080,
        url_path: str = "webhook",
        webhook_url: Optional[str] = None,
        cert: Optional[str] = None,
        max_connections: int = 40,
        allowed_updates: Optional[List[str]] = None,
        drop_pending_updates: bool = False,
        secret_token: Optional[str] = None,
    ) -> None:
        """Inicia el webhook.

        Args:
            listen: Dirección IP a escuchar
            port: Puerto a escuchar
            url_path: Path del webhook
            webhook_url: URL completa del webhook
            cert: Certificado SSL
            max_connections: Conexiones máximas
            allowed_updates: Updates permitidos
            drop_pending_updates: Descartar updates pendientes
            secret_token: Token secreto para verificación
        """
        if not webhook_url:
            webhook_url = f"https://{listen}:{port}/{url_path}"

        if self._application and hasattr(self._application, 'run_webhook'):
            if HAS_TELEGRAM and self._bot:
                await self._bot.set_webhook(
                    url=webhook_url,
                    certificate=cert,
                    max_connections=max_connections,
                    allowed_updates=allowed_updates,
                    drop_pending_updates=drop_pending_updates,
                    secret_token=secret_token,
                )

            self._application.run_webhook(
                listen=listen,
                port=port,
                url_path=url_path,
                webhook_url=webhook_url,
                cert=cert,
                max_connections=max_connections,
                allowed_updates=allowed_updates,
                drop_pending_updates=drop_pending_updates,
                secret_token=secret_token,
            )
            self._running = True

        self._webhook_info = {
            "url": webhook_url,
            "has_custom_certificate": cert is not None,
            "max_connections": max_connections,
            "allowed_updates": allowed_updates,
        }

    async def stop(self) -> None:
        """Detiene el webhook."""
        if self._running and self._bot and HAS_TELEGRAM:
            try:
                await self._bot.delete_webhook()
            except Exception:
                pass

        if self._application and hasattr(self._application, 'stop'):
            await self._application.stop()

        self._running = False

    async def get_webhook_info(self) -> Dict[str, Any]:
        """Obtiene información del webhook actual.

        Returns:
            Información del webhook
        """
        if self._bot and HAS_TELEGRAM:
            try:
                return await self._bot.get_webhook_info()
            except Exception:
                pass
        return self._webhook_info


class WebhookHandler:
    """Handler para procesar updates de webhook."""

    def __init__(
        self,
        application: Any,
        bot: Optional[Any] = None,
        secret_token: Optional[str] = None,
    ):
        """Inicializa el handler.

        Args:
            application: Aplicación PTB
            bot: Bot de Telegram
            secret_token: Token secreto para verificación
        """
        self._application = application
        self._bot = bot
        self._secret_token = secret_token

    async def handle(
        self,
        request: Any,
        body: bytes,
    ) -> Any:
        """Maneja un request de webhook.

        Args:
            request: Request de FastAPI/uvicorn
            body: Body del request

        Returns:
            Respuesta
        """
        if self._secret_token:
            secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if secret != self._secret_token:
                return {"error": "Unauthorized"}, 401

        if not HAS_TELEGRAM:
            return {"error": "PTB not available"}, 500

        import json
        from telegram import Update

        try:
            data = json.loads(body)
            update = Update.de_json(data, self._bot)
        except Exception as e:
            return {"error": str(e)}, 400

        if self._application and hasattr(self._application, 'process_update'):
            await self._application.process_update(update)

        return {"ok": True}, 200

    async def handle_fastapi(
        self,
        request: Any,
    ) -> Dict[str, Any]:
        """Maneja un request de FastAPI.

        Args:
            request: Request de FastAPI

        Returns:
            Respuesta
        """
        body = await request.body()
        return await self.handle(request, body)


__all__ = ["WebhookRunner", "WebhookHandler"]
