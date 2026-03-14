"""Bridge para Application PTB."""

from typing import Any, Callable, Dict, List, Optional, Type

try:
    from telegram.ext import Application as PTBApplication
    HAS_TELEGRAM_EXT = True
except ImportError:
    HAS_TELEGRAM_EXT = False
    PTBApplication = None


class ApplicationBridge:
    """Bridge para integrar la app con Application de PTB."""
    
    def __init__(self, application: Optional[Any] = None):
        """Inicializa el bridge.
        
        Args:
            application: Application de PTB (opcional)
        """
        self._application = application
        self._handlers: Dict[str, List[Any]] = {
            "command": [],
            "message": [],
            "callback_query": [],
            "inline_query": [],
            "chosen_inline_result": [],
            "error": [],
        }
        self._middlewares: List[Any] = []
        self._post_init: Optional[Callable] = None
        self._post_shutdown: Optional[Callable] = None
    
    def set_application(self, application: Any) -> None:
        """Define la aplicación PTB.
        
        Args:
            application: Application de PTB
        """
        self._application = application
    
    def add_command_handler(
        self,
        handler: Any,
        commands: Optional[List[str]] = None
    ) -> None:
        """Agrega un command handler.
        
        Args:
            handler: Handler a agregar
            commands: Lista de comandos (opcional)
        """
        self._handlers["command"].append({
            "handler": handler,
            "commands": commands,
        })
        if self._application and HAS_TELEGRAM_EXT:
            if commands:
                for cmd in commands:
                    self._application.add_handler(handler, cmd)
            else:
                self._application.add_handler(handler)
    
    def add_message_handler(self, handler: Any) -> None:
        """Agrega un message handler.
        
        Args:
            handler: Handler a agregar
        """
        self._handlers["message"].append(handler)
        if self._application and HAS_TELEGRAM_EXT:
            self._application.add_handler(handler)
    
    def add_callback_query_handler(self, handler: Any) -> None:
        """Agrega un callback query handler.
        
        Args:
            handler: Handler a agregar
        """
        self._handlers["callback_query"].append(handler)
        if self._application and HAS_TELEGRAM_EXT:
            self._application.add_handler(handler)
    
    def add_inline_query_handler(self, handler: Any) -> None:
        """Agrega un inline query handler.
        
        Args:
            handler: Handler a agregar
        """
        self._handlers["inline_query"].append(handler)
        if self._application and HAS_TELEGRAM_EXT:
            self._application.add_handler(handler)
    
    def add_error_handler(self, handler: Callable) -> None:
        """Agrega un error handler.
        
        Args:
            handler: Handler de errores
        """
        self._handlers["error"].append(handler)
        if self._application and HAS_TELEGRAM_EXT:
            self._application.add_error_handler(handler)
    
    def add_middleware(self, middleware: Any) -> None:
        """Agrega un middleware.
        
        Args:
            middleware: Middleware a agregar
        """
        self._middlewares.append(middleware)
        if self._application and HAS_TELEGRAM_EXT:
            self._application.add_middleware(middleware)
    
    def set_post_init(self, callback: Callable) -> None:
        """Define callback post-init.
        
        Args:
            callback: Función a ejecutar post-init
        """
        self._post_init = callback
        if self._application and HAS_TELEGRAM_EXT:
            self._application.post_init = callback
    
    def set_post_shutdown(self, callback: Callable) -> None:
        """Define callback post-shutdown.
        
        Args:
            callback: Función a ejecutar post-shutdown
        """
        self._post_shutdown = callback
        if self._application and HAS_TELEGRAM_EXT:
            self._application.post_shutdown = callback
    
    def get_handlers(self, handler_type: str) -> List[Any]:
        """Obtiene los handlers de un tipo.
        
        Args:
            handler_type: Tipo de handler
            
        Returns:
            Lista de handlers
        """
        return self._handlers.get(handler_type, [])
    
    def get_all_handlers(self) -> Dict[str, List[Any]]:
        """Obtiene todos los handlers.
        
        Returns:
            Diccionario de handlers
        """
        return self._handlers.copy()
    
    def get_middlewares(self) -> List[Any]:
        """Obtiene los middlewares.
        
        Returns:
            Lista de middlewares
        """
        return self._middlewares.copy()
    
    async def initialize(self) -> None:
        """Inicializa la aplicación."""
        if self._application and HAS_TELEGRAM_EXT:
            await self._application.initialize()
    
    async def start(self) -> None:
        """Inicia la aplicación."""
        if self._application and HAS_TELEGRAM_EXT:
            await self._application.start()
    
    async def stop(self) -> None:
        """Detiene la aplicación."""
        if self._application and HAS_TELEGRAM_EXT:
            await self._application.stop()
    
    async def shutdown(self) -> None:
        """Apaga la aplicación."""
        if self._application and HAS_TELEGRAM_EXT:
            await self._application.shutdown()
    
    def run_webhook(
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
        """Ejecuta la aplicación con webhook.
        
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
        if self._application and HAS_TELEGRAM_EXT:
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
    
    def run_polling(
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
        """Ejecuta la aplicación con polling.
        
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
        if self._application and HAS_TELEGRAM_EXT:
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


class ApplicationBuilderBridge:
    """Builder para crear Application de PTB con integración."""
    
    def __init__(self):
        """Inicializa el builder."""
        self._token: Optional[str] = None
        self._application: Optional[Any] = None
        self._bridge: Optional[ApplicationBridge] = None
    
    def token(self, token: str) -> "ApplicationBuilderBridge":
        """Define el token del bot.
        
        Args:
            token: Token del bot
            
        Returns:
            Self
        """
        self._token = token
        return self
    
    def build(self) -> ApplicationBridge:
        """Construye el bridge.
        
        Returns:
            ApplicationBridge
        """
        if HAS_TELEGRAM_EXT:
            from telegram.ext import ApplicationBuilder
            
            self._application = (
                ApplicationBuilder()
                .token(self._token or "")
                .build()
            )
        
        self._bridge = ApplicationBridge(self._application)
        return self._bridge
    
    def get_bridge(self) -> Optional[ApplicationBridge]:
        """Obtiene el bridge.
        
        Returns:
            ApplicationBridge
        """
        return self._bridge


__all__ = ["ApplicationBridge", "ApplicationBuilderBridge"]
