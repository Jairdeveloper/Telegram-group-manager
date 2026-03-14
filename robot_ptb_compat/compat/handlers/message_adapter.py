"""Adapter para mensajes PTB."""

from typing import Any, Callable, List, Optional

from robot_ptb_compat.compat.handlers.base_adapter import BaseHandlerAdapter


class MessageAdapter(BaseHandlerAdapter):
    """Adaptador para MessageHandler de PTB."""
    
    def __init__(
        self,
        callback: Callable,
        filters: Optional[Any] = None,
        pass_update_queue: bool = False,
        pass_job_queue: bool = False,
        pass_user_data: bool = True,
        pass_chat_data: bool = True,
        message_types: Optional[List[str]] = None,
    ):
        """Inicializa el adaptador de mensajes.
        
        Args:
            callback: Función callback a ejecutar
            filters: Filtros PTB
            pass_update_queue: Pasar queue de updates
            pass_job_queue: Pasar job queue
            pass_user_data: Pasar user data
            pass_chat_data: Pasar chat data
            message_types: Tipos de mensaje a manejar (text, photo, etc.)
        """
        super().__init__(
            callback=callback,
            filters=filters,
            pass_update_queue=pass_update_queue,
            pass_job_queue=pass_job_queue,
            pass_user_data=pass_user_data,
            pass_chat_data=pass_chat_data,
        )
        self.message_types = message_types or ["text"]
    
    async def handle(self, update: Any, context: Any) -> Any:
        """Maneja el mensaje.
        
        Args:
            update: Update de Telegram
            context: Contexto del handler
            
        Returns:
            Resultado del callback
        """
        if not self.check_filter(update):
            return None
        
        message = update.message if hasattr(update, 'message') else None
        if not message:
            return None
        
        if not self._check_message_type(message):
            return None
        
        return await self._execute_callback(update, context)
    
    def _check_message_type(self, message: Any) -> bool:
        """Verifica si el tipo de mensaje es soportado.
        
        Args:
            message: Mensaje a verificar
            
        Returns:
            True si el tipo es soportado
        """
        if not self.message_types:
            return True
        
        for msg_type in self.message_types:
            if hasattr(message, msg_type) and getattr(message, msg_type):
                return True
        
        return False
    
    def get_message_types(self) -> List[str]:
        """Retorna los tipos de mensaje configurados.
        
        Returns:
            Lista de tipos de mensaje
        """
        return self.message_types
    
    def add_message_type(self, msg_type: str) -> None:
        """Agrega un tipo de mensaje.
        
        Args:
            msg_type: Tipo de mensaje a agregar
        """
        if msg_type not in self.message_types:
            self.message_types.append(msg_type)


class MessageFilters:
    """Filtros comunes para mensajes."""
    
    @staticmethod
    def text(update: Any) -> bool:
        """Filtro para mensajes de texto."""
        return (
            hasattr(update, 'message') and
            update.message and
            hasattr(update.message, 'text') and
            update.message.text
        )
    
    @staticmethod
    def photo(update: Any) -> bool:
        """Filtro para mensajes de foto."""
        return (
            hasattr(update, 'message') and
            update.message and
            hasattr(update.message, 'photo') and
            update.message.photo
        )
    
    @staticmethod
    def document(update: Any) -> bool:
        """Filtro para mensajes de documento."""
        return (
            hasattr(update, 'message') and
            update.message and
            hasattr(update.message, 'document') and
            update.message.document
        )
    
    @staticmethod
    def video(update: Any) -> bool:
        """Filtro para mensajes de video."""
        return (
            hasattr(update, 'message') and
            update.message and
            hasattr(update.message, 'video') and
            update.message.video
        )
    
    @staticmethod
    def voice(update: Any) -> bool:
        """Filtro para mensajes de voz."""
        return (
            hasattr(update, 'message') and
            update.message and
            hasattr(update.message, 'voice') and
            update.message.voice
        )
    
    @staticmethod
    def audio(update: Any) -> bool:
        """Filtro para mensajes de audio."""
        return (
            hasattr(update, 'message') and
            update.message and
            hasattr(update.message, 'audio') and
            update.message.audio
        )
    
    @staticmethod
    def location(update: Any) -> bool:
        """Filtro para mensajes de ubicación."""
        return (
            hasattr(update, 'message') and
            update.message and
            hasattr(update.message, 'location') and
            update.message.location
        )
    
    @staticmethod
    def venue(update: Any) -> bool:
        """Filtro para mensajes de venue."""
        return (
            hasattr(update, 'message') and
            update.message and
            hasattr(update.message, 'venue') and
            update.message.venue
        )
    
    @staticmethod
    def contact(update: Any) -> bool:
        """Filtro para mensajes de contacto."""
        return (
            hasattr(update, 'message') and
            update.message and
            hasattr(update.message, 'contact') and
            update.message.contact
        )
    
    @staticmethod
    def sticker(update: Any) -> bool:
        """Filtro para mensajes de sticker."""
        return (
            hasattr(update, 'message') and
            update.message and
            hasattr(update.message, 'sticker') and
            update.message.sticker
        )
    
    @staticmethod
    def command(update: Any) -> bool:
        """Filtro para mensajes que son comandos."""
        return (
            MessageFilters.text(update) and
            update.message.text.strip().startswith('/')
        )


__all__ = ["MessageAdapter", "MessageFilters"]
