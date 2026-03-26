"""Application Builder para PTB."""

from typing import Any, Callable, Optional, Type

try:
    from telegram.ext import ApplicationBuilder as PTBApplicationBuilder
    from telegram.ext import Application as PTBApplication
    HAS_TELEGRAM_EXT = True
except ImportError:
    HAS_TELEGRAM_EXT = False
    PTBApplicationBuilder = None
    PTBApplication = None


class CompatApplicationBuilder:
    """Builder compatible con PTB que integra la app."""

    def __init__(self, token: Optional[str] = None):
        """Inicializa el builder.

        Args:
            token: Token del bot de Telegram
        """
        self._token = token
        self._ptb_builder = None
        self._manager_bot = None
        self._custom_handlers = []
        self._middlewares = []
        self._post_init_callback = None
        self._post_shutdown_callback = None
        self._bot_settings = {}
        self._application = None

        if HAS_TELEGRAM_EXT:
            if token:
                self._ptb_builder = PTBApplicationBuilder().token(token)

    def token(self, token: str) -> "CompatApplicationBuilder":
        """Define el token del bot.

        Args:
            token: Token del bot

        Returns:
            Self
        """
        self._token = token
        if HAS_TELEGRAM_EXT and not self._ptb_builder:
            self._ptb_builder = PTBApplicationBuilder().token(token)
        return self

    def manager_bot(self, manager_bot: Any) -> "CompatApplicationBuilder":
        """Integra ManagerBot.

        Args:
            manager_bot: Instancia de ManagerBot

        Returns:
            Self
        """
        self._manager_bot = manager_bot
        return self

    def bot_username(self, username: str) -> "CompatApplicationBuilder":
        """Define el username del bot.

        Args:
            username: Username del bot

        Returns:
            Self
        """
        self._bot_settings["username"] = username
        if self._ptb_builder:
            self._ptb_builder.bot_username(username)
        return self

    def bot_short_description(self, description: str) -> "CompatApplicationBuilder":
        """Define la descripción corta del bot.

        Args:
            description: Descripción corta

        Returns:
            Self
        """
        self._bot_settings["short_description"] = description
        if self._ptb_builder:
            self._ptb_builder.bot_short_description(description)
        return self

    def bot_description(self, description: str) -> "CompatApplicationBuilder":
        """Define la descripción del bot.

        Args:
            description: Descripción

        Returns:
            Self
        """
        self._bot_settings["description"] = description
        if self._ptb_builder:
            self._ptb_builder.bot_description(description)
        return self

    def rate_limiter(self, rate_limiter: Any) -> "CompatApplicationBuilder":
        """Define el rate limiter.

        Args:
            rate_limiter: Rate limiter

        Returns:
            Self
        """
        if self._ptb_builder:
            self._ptb_builder.rate_limiter(rate_limiter)
        return self

    def persistence(self, persistence: Any) -> "CompatApplicationBuilder":
        """Define la persistencia.

        Args:
            persistence: Persistencia

        Returns:
            Self
        """
        if self._ptb_builder:
            self._ptb_builder.persistence(persistence)
        return self

    def post_init(self, callback: Callable) -> "CompatApplicationBuilder":
        """Define callback post-init.

        Args:
            callback: Función a ejecutar post-init

        Returns:
            Self
        """
        self._post_init_callback = callback
        if self._ptb_builder:
            self._ptb_builder.post_init(callback)
        return self

    def post_shutdown(self, callback: Callable) -> "CompatApplicationBuilder":
        """Define callback post-shutdown.

        Args:
            callback: Función a ejecutar post-shutdown

        Returns:
            Self
        """
        self._post_shutdown_callback = callback
        if self._ptb_builder:
            self._ptb_builder.post_shutdown(callback)
        return self

    def add_handler(self, handler: Any, group: int = 0) -> "CompatApplicationBuilder":
        """Agrega un handler.

        Args:
            handler: Handler a agregar
            group: Grupo del handler

        Returns:
            Self
        """
        self._custom_handlers.append({"handler": handler, "group": group})
        return self

    def add_middleware(self, middleware: Any) -> "CompatApplicationBuilder":
        """Agrega un middleware.

        Args:
            middleware: Middleware a agregar

        Returns:
            Self
        """
        self._middlewares.append(middleware)
        if self._ptb_builder:
            self._ptb_builder.middleware(middleware)
        return self

    def build(self) -> Any:
        """Construye la aplicación.

        Returns:
            Application PTB o wrapper
        """
        if HAS_TELEGRAM_EXT and self._ptb_builder:
            self._application = self._ptb_builder.build()

            for handler_config in self._custom_handlers:
                self._application.add_handler(
                    handler_config["handler"],
                    handler_config["group"]
                )

            return self._application

        return self._create_fallback_application()

    def _create_fallback_application(self) -> Any:
        """Crea una aplicación fallback si PTB no está disponible."""
        return FallbackApplication(
            token=self._token,
            manager_bot=self._manager_bot,
            handlers=self._custom_handlers,
            middlewares=self._middlewares,
        )


class FallbackApplication:
    """Aplicación fallback cuando PTB no está disponible."""

    def __init__(
        self,
        token: str,
        manager_bot: Optional[Any] = None,
        handlers: list = None,
        middlewares: list = None
    ):
        self.token = token
        self.manager_bot = manager_bot
        self.handlers = handlers or []
        self.middlewares = middlewares or []
        self._running = False

    async def initialize(self) -> None:
        """Inicializa la aplicación."""
        self._running = True

    async def start(self) -> None:
        """Inicia la aplicación."""
        self._running = True

    async def stop(self) -> None:
        """Detiene la aplicación."""
        self._running = False

    async def shutdown(self) -> None:
        """Apaga la aplicación."""
        self._running = False

    def add_handler(self, handler: Any, group: int = 0) -> None:
        """Agrega un handler."""
        self.handlers.append({"handler": handler, "group": group})

    def add_middleware(self, middleware: Any) -> None:
        """Agrega un middleware."""
        self.middlewares.append(middleware)

    def run_webhook(self, **kwargs) -> None:
        """Ejecuta con webhook."""
        pass

    def run_polling(self, **kwargs) -> None:
        """Ejecuta con polling."""
        pass


__all__ = ["CompatApplicationBuilder", "FallbackApplication"]
