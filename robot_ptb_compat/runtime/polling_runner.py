"""Polling Runner para la aplicación."""

import asyncio
from typing import Any, Callable, Dict, List, Optional

try:
    from telegram import Bot
    from telegram.error import TelegramError
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    Bot = None
    TelegramError = Exception


class PollingRunner:
    """Runner para ejecutar la aplicación con polling."""

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
        self._running = False
        self._polling_task: Optional[asyncio.Task] = None

    @property
    def bot(self) -> Optional[Any]:
        """Obtiene el bot."""
        return self._bot

    @property
    def is_running(self) -> bool:
        """Retorna si el runner está ejecutándose."""
        return self._running

    async def start(
        self,
        poll_interval: float = 1.0,
        timeout: int = 10,
        bootstrap_retries: int = -1,
        drop_pending_updates: bool = False,
        allowed_updates: Optional[List[str]] = None,
        listen: str = "127.0.0.1",
        port: int = 8000,
        url_path: str = "",
        cert: Optional[str] = None,
        webhook_url: Optional[str] = None,
    ) -> None:
        """Inicia el polling.

        Args:
            poll_interval: Intervalo de polling
            timeout: Timeout
            bootstrap_retries: Reintentos de bootstrap
            drop_pending_updates: Descartar updates pendientes
            allowed_updates: Updates permitidos
            listen: Dirección IP
            port: Puerto
            url_path: Path URL
            cert: Certificado
            webhook_url: URL webhook
        """
        if self._application and hasattr(self._application, 'run_polling'):
            self._application.run_polling(
                poll_interval=poll_interval,
                timeout=timeout,
                bootstrap_retries=bootstrap_retries,
                drop_pending_updates=drop_pending_updates,
                allowed_updates=allowed_updates,
                listen=listen,
                port=port,
                url_path=url_path,
                cert=cert,
                webhook_url=webhook_url,
            )
            self._running = True
        else:
            await self._start_polling_loop(
                poll_interval=poll_interval,
                timeout=timeout,
                allowed_updates=allowed_updates,
                drop_pending_updates=drop_pending_updates,
            )

    async def _start_polling_loop(
        self,
        poll_interval: float,
        timeout: int,
        allowed_updates: Optional[List[str]],
        drop_pending_updates: bool,
    ) -> None:
        """Inicia el loop de polling manual."""
        if not self._bot or not HAS_TELEGRAM:
            return

        self._running = True

        while self._running:
            try:
                updates = await self._bot.get_updates(
                    timeout=timeout,
                    allowed_updates=allowed_updates,
                )

                for update in updates:
                    if self._application and hasattr(self._application, 'process_update'):
                        await self._application.process_update(update)

                await asyncio.sleep(poll_interval)

            except TelegramError as e:
                if e.message == "Conflict":
                    break
                await asyncio.sleep(poll_interval)
            except Exception:
                await asyncio.sleep(poll_interval)

    async def stop(self) -> None:
        """Detiene el polling."""
        self._running = False

        if self._polling_task:
            self._polling_task.cancel()
            try:
                await self._polling_task
            except asyncio.CancelledError:
                pass

        if self._application and hasattr(self._application, 'stop'):
            await self._application.stop()


class PollingHandler:
    """Handler para procesar updates de polling."""

    def __init__(
        self,
        application: Any,
        bot: Any,
    ):
        """Inicializa el handler.

        Args:
            application: Aplicación PTB
            bot: Bot de Telegram
        """
        self._application = application
        self._bot = bot

    async def process_update(self, update: Any) -> None:
        """Procesa un update.

        Args:
            update: Update de Telegram
        """
        if self._application and hasattr(self._application, 'process_update'):
            await self._application.process_update(update)

    async def poll(
        self,
        poll_interval: float = 1.0,
        timeout: int = 10,
        allowed_updates: Optional[List[str]] = None,
    ) -> None:
        """Inicia el polling.

        Args:
            poll_interval: Intervalo de polling
            timeout: Timeout
            allowed_updates: Updates permitidos
        """
        offset = None

        while True:
            try:
                updates = await self._bot.get_updates(
                    offset=offset,
                    timeout=timeout,
                    allowed_updates=allowed_updates,
                )

                for update in updates:
                    await self.process_update(update)
                    offset = update.update_id + 1

                await asyncio.sleep(poll_interval)

            except Exception:
                await asyncio.sleep(poll_interval)


__all__ = ["PollingRunner", "PollingHandler"]
