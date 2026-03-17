"""Adapter para callbacks PTB."""

from typing import Any, Callable, Optional
import re

from robot_ptb_compat.compat.handlers.base_adapter import BaseHandlerAdapter


class CallbackAdapter(BaseHandlerAdapter):
    """Adaptador para CallbackQueryHandler de PTB."""
    
    def __init__(
        self,
        callback: Callable,
        filters: Optional[Any] = None,
        pass_update_queue: bool = False,
        pass_job_queue: bool = False,
        pass_user_data: bool = True,
        pass_chat_data: bool = True,
        pattern: Optional[str] = None,
    ):
        """Inicializa el adaptador de callbacks.
        
        Args:
            callback: Función callback a ejecutar
            filters: Filtros PTB
            pass_update_queue: Pasar queue de updates
            pass_job_queue: Pasar job queue
            pass_user_data: Pasar user data
            pass_chat_data: Pasar chat data
            pattern: Pattern regex para filtrar callback_data
        """
        super().__init__(
            callback=callback,
            filters=filters,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
        )
        self.pattern = pattern
        if pattern:
            self._pattern = re.compile(pattern)
        else:
            self._pattern = None
    
    async def handle(self, update: Any, context: Any) -> Any:
        """Maneja el callback query.
        
        Args:
            update: Update de Telegram
            context: Contexto del handler
            
        Returns:
            Resultado del callback
        """
        if not self.check_filter(update):
            return None
        
        callback_query = update.callback_query if hasattr(update, 'callback_query') else None
        if not callback_query:
            return None
        
        if self._pattern:
            data = callback_query.data if hasattr(callback_query, 'data') else ""
            if not data or not self._pattern.match(data):
                return None
        
        context.callback_query = callback_query
        context.data = callback_query.data if hasattr(callback_query, 'data') else None
        
        return await self._execute_callback(update, context)
    
    def set_pattern(self, pattern: str) -> None:
        """Define un nuevo pattern.
        
        Args:
            pattern: Pattern regex
        """
        self.pattern = pattern
        if pattern:
            self._pattern = re.compile(pattern)
        else:
            self._pattern = None


def prefix_pattern(prefix: str) -> str:
    """Build a regex pattern that matches a prefix with optional suffix."""
    escaped = re.escape(prefix)
    return f"^{escaped}(:.*)?$"


class CallbackPrefixAdapter(CallbackAdapter):
    """Convenience adapter for prefix-based callback routing."""

    def __init__(self, prefix: str, callback: Callable, **kwargs):
        super().__init__(callback=callback, pattern=prefix_pattern(prefix), **kwargs)


class InlineQueryAdapter(BaseHandlerAdapter):
    """Adaptador para InlineQueryHandler de PTB."""
    
    def __init__(
        self,
        callback: Callable,
        filters: Optional[Any] = None,
        pass_update_queue: bool = False,
        pass_job_queue: bool = False,
        pass_user_data: bool = True,
        pass_chat_data: bool = True,
        pattern: Optional[str] = None,
    ):
        """Inicializa el adaptador de inline queries.
        
        Args:
            callback: Función callback a ejecutar
            filters: Filtros PTB
            pass_update_queue: Pasar queue de updates
            pass_job_queue: Pasar job queue
            pass_user_data: Pasar user data
            pass_chat_data: Pasar chat data
            pattern: Pattern regex para filtrar query
        """
        super().__init__(
            callback=callback,
            filters=filters,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
        )
        self.pattern = pattern
        if pattern:
            import re
            self._pattern = re.compile(pattern)
        else:
            self._pattern = None
    
    async def handle(self, update: Any, context: Any) -> Any:
        """Maneja el inline query.
        
        Args:
            update: Update de Telegram
            context: Contexto del handler
            
        Returns:
            Resultado del callback
        """
        if not self.check_filter(update):
            return None
        
        inline_query = update.inline_query if hasattr(update, 'inline_query') else None
        if not inline_query:
            return None
        
        if self._pattern:
            query = inline_query.query if hasattr(inline_query, 'query') else ""
            if not self._pattern.match(query):
                return None
        
        context.inline_query = inline_query
        context.query = inline_query.query if hasattr(inline_query, 'query') else ""
        
        return await self._execute_callback(update, context)


class ChosenInlineResultAdapter(BaseHandlerAdapter):
    """Adaptador para ChosenInlineResultHandler de PTB."""
    
    def __init__(
        self,
        callback: Callable,
        filters: Optional[Any] = None,
        pass_update_queue: bool = False,
        pass_job_queue: bool = False,
        pass_user_data: bool = True,
        pass_chat_data: bool = True,
    ):
        """Inicializa el adaptador de chosen inline results.
        
        Args:
            callback: Función callback a ejecutar
            filters: Filtros PTB
            pass_update_queue: Pasar queue de updates
            pass_job_queue: Pasar job queue
            pass_user_data: Pasar user data
            pass_chat_data: Pasar chat data
        """
        super().__init__(
            callback=callback,
            filters=filters,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
        )
    
    async def handle(self, update: Any, context: Any) -> Any:
        """Maneja el chosen inline result.
        
        Args:
            update: Update de Telegram
            context: Contexto del handler
            
        Returns:
            Resultado del callback
        """
        if not self.check_filter(update):
            return None
        
        chosen_inline_result = update.chosen_inline_result if hasattr(update, 'chosen_inline_result') else None
        if not chosen_inline_result:
            return None
        
        context.chosen_inline_result = chosen_inline_result
        context.result_id = chosen_inline_result.result_id if hasattr(chosen_inline_result, 'result_id') else None
        context.query = chosen_inline_result.query if hasattr(chosen_inline_result, 'query') else ""
        
        return await self._execute_callback(update, context)


__all__ = [
    "CallbackAdapter",
    "CallbackPrefixAdapter",
    "InlineQueryAdapter",
    "ChosenInlineResultAdapter",
    "prefix_pattern",
]
