"""Base adapter para handlers PTB."""

from typing import Any, Callable, Optional
from abc import ABC, abstractmethod

try:
    from telegram import Update
    from telegram.ext import CallbackContext
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    Update = None
    CallbackContext = None


class BaseHandlerAdapter(ABC):
    """Clase base para adaptadores de handlers PTB."""
    
    def __init__(
        self,
        callback: Optional[Callable] = None,
        filters: Optional[Any] = None,
        pass_update_queue: bool = False,
        pass_job_queue: bool = False,
        pass_user_data: bool = True,
        pass_chat_data: bool = True,
    ):
        """Inicializa el adaptador.
        
        Args:
            callback: Función callback a ejecutar
            filters: Filtros PTB (opcional)
            pass_update_queue: Pasar queue de updates
            pass_job_queue: Pasar job queue
            pass_user_data: Pasar user data
            pass_chat_data: Pasar chat data
        """
        self.callback = callback
        self.filters = filters
        self.pass_update_queue = pass_update_queue
        self.pass_job_queue = pass_job_queue
        self.pass_user_data = pass_user_data
        self.pass_chat_data = pass_chat_data
    
    @abstractmethod
    async def handle(self, update: Any, context: Any) -> Any:
        """Maneja el update.
        
        Args:
            update: Update de Telegram
            context: Contexto del handler
            
        Returns:
            Resultado del callback
        """
        pass
    
    def check_filter(self, update: Any) -> bool:
        """Verifica si el update pasa los filtros.
        
        Args:
            update: Update a verificar
            
        Returns:
            True si pasa los filtros
        """
        if self.filters is None:
            return True
        
        if hasattr(self.filters, 'check'):
            return self.filters.check(update)
        
        return True
    
    async def _execute_callback(
        self,
        update: Any,
        context: Any,
        *args,
        **kwargs
    ) -> Any:
        """Ejecuta el callback con los parámetros apropiados.
        
        Args:
            update: Update de Telegram
            context: Contexto del handler
            *args: Argumentos adicionales
            **kwargs: Argumentos keyword adicionales
            
        Returns:
            Resultado del callback
        """
        if self.callback is None:
            return None
        
        import inspect
        sig = inspect.signature(self.callback)
        params = sig.parameters
        
        call_args = []
        call_kwargs = {}
        
        if 'update' in params:
            call_args.append(update)
        if 'context' in params:
            call_args.append(context)
        
        for arg in args:
            call_args.append(arg)
        
        for key, value in kwargs.items():
            if key in params:
                call_kwargs[key] = value
        
        if inspect.iscoroutinefunction(self.callback):
            return await self.callback(*call_args, **call_kwargs)
        else:
            return self.callback(*call_args, **call_kwargs)
    
    def get_handler_type(self) -> str:
        """Retorna el tipo de handler.
        
        Returns:
            Tipo de handler
        """
        return self.__class__.__name__.replace('Adapter', '')


__all__ = ["BaseHandlerAdapter"]
