"""Adapter para filtros PTB."""

import re
from typing import Any, Callable, List, Optional


class FiltersAdapter:
    """Adaptador para filtros de PTB."""
    
    @staticmethod
    def text() -> "TextFilter":
        """Filtro para mensajes de texto."""
        return TextFilter()
    
    @staticmethod
    def command() -> "CommandFilter":
        """Filtro para comandos."""
        return CommandFilter()
    
    @staticmethod
    def regex(pattern: str) -> "RegexFilter":
        """Filtro por regex.
        
        Args:
            pattern: Pattern regex
            
        Returns:
            RegexFilter
        """
        return RegexFilter(pattern)
    
    @staticmethod
    def photo() -> "PhotoFilter":
        """Filtro para fotos."""
        return PhotoFilter()
    
    @staticmethod
    def video() -> "VideoFilter":
        """Filtro para videos."""
        return VideoFilter()
    
    @staticmethod
    def document() -> "DocumentFilter":
        """Filtro para documentos."""
        return DocumentFilter()
    
    @staticmethod
    def audio() -> "AudioFilter":
        """Filtro para audio."""
        return AudioFilter()
    
    @staticmethod
    def voice() -> "VoiceFilter":
        """Filtro para voz."""
        return VoiceFilter()
    
    @staticmethod
    def sticker() -> "StickerFilter":
        """Filtro para stickers."""
        return StickerFilter()
    
    @staticmethod
    def location() -> "LocationFilter":
        """Filtro para ubicación."""
        return LocationFilter()
    
    @staticmethod
    def venue() -> "VenueFilter":
        """Filtro para venues."""
        return VenueFilter()
    
    @staticmethod
    def contact() -> "ContactFilter":
        """Filtro para contactos."""
        return ContactFilter()
    
    @staticmethod
    def private() -> "ChatTypeFilter":
        """Filtro para chats privados."""
        return ChatTypeFilter("private")
    
    @staticmethod
    def group() -> "ChatTypeFilter":
        """Filtro para grupos."""
        return ChatTypeFilter("group")
    
    @staticmethod
    def supergroup() -> "ChatTypeFilter":
        """Filtro para supergrupos."""
        return ChatTypeFilter("supergroup")
    
    @staticmethod
    def channel() -> "ChatTypeFilter":
        """Filtro para canales."""
        return ChatTypeFilter("channel")
    
    @staticmethod
    def forwarded() -> "ForwardedFilter":
        """Filtro para mensajes reenviados."""
        return ForwardedFilter()
    
    @staticmethod
    def game() -> "GameFilter":
        """Filtro para juegos."""
        return GameFilter()
    
    @staticmethod
    def invoice() -> "InvoiceFilter":
        """Filtro para facturas."""
        return InvoiceFilter()
    
    @staticmethod
    def successful_payment() -> "SuccessfulPaymentFilter":
        """Filtro para pagos exitosos."""
        return SuccessfulPaymentFilter()
    
    @staticmethod
    def _and(*filters: "FilterType") -> "_CombinedFilter":
        """Combina filtros con AND."""
        return _CombinedFilter("AND", filters)
    
    @staticmethod
    def _or(*filters: "FilterType") -> "_CombinedFilter":
        """Combina filtros con OR."""
        return _CombinedFilter("OR", filters)
    
    @staticmethod
    def _not(filter: "FilterType") -> "_NotFilter":
        """Niega un filtro."""
        return _NotFilter(filter)


FilterType = Any


class FilterBase:
    """Clase base para filtros."""
    
    def check(self, update: Any) -> bool:
        """Verifica si el update pasa el filtro.
        
        Args:
            update: Update a verificar
            
        Returns:
            True si pasa el filtro
        """
        return True
    
    def __and__(self, other: "FilterType") -> "_CombinedFilter":
        return FiltersAdapter._and(self, other)
    
    def __or__(self, other: "FilterType") -> "_CombinedFilter":
        return FiltersAdapter._or(self, other)
    
    def __invert__(self) -> "_NotFilter":
        return FiltersAdapter._not(self)


class TextFilter(FilterBase):
    """Filtro para mensajes de texto."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'text', None)


class CommandFilter(FilterBase):
    """Filtro para comandos."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        if not message:
            return False
        text = getattr(message, 'text', None)
        return text and text.strip().startswith('/')


class RegexFilter(FilterBase):
    """Filtro por regex."""
    
    def __init__(self, pattern: str):
        self.pattern = re.compile(pattern)
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        text = getattr(message, 'text', None)
        if not text:
            return False
        return bool(self.pattern.search(text))


class PhotoFilter(FilterBase):
    """Filtro para fotos."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'photo', None)


class VideoFilter(FilterBase):
    """Filtro para videos."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'video', None)


class DocumentFilter(FilterBase):
    """Filtro para documentos."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'document', None)


class AudioFilter(FilterBase):
    """Filtro para audio."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'audio', None)


class VoiceFilter(FilterBase):
    """Filtro para voz."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'voice', None)


class StickerFilter(FilterBase):
    """Filtro para stickers."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'sticker', None)


class LocationFilter(FilterBase):
    """Filtro para ubicación."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'location', None)


class VenueFilter(FilterBase):
    """Filtro para venues."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'venue', None)


class ContactFilter(FilterBase):
    """Filtro para contactos."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'contact', None)


class ChatTypeFilter(FilterBase):
    """Filtro por tipo de chat."""
    
    def __init__(self, chat_type: str):
        self.chat_type = chat_type
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        if not message:
            return False
        chat = getattr(message, 'chat', None)
        if not chat:
            return False
        return getattr(chat, 'type', None) == self.chat_type


class ForwardedFilter(FilterBase):
    """Filtro para mensajes reenviados."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        if not message:
            return False
        return getattr(message, 'forward_date', None) is not None


class GameFilter(FilterBase):
    """Filtro para juegos."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'game', None)


class InvoiceFilter(FilterBase):
    """Filtro para facturas."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'invoice', None)


class SuccessfulPaymentFilter(FilterBase):
    """Filtro para pagos exitosos."""
    
    def check(self, update: Any) -> bool:
        message = getattr(update, 'message', None)
        return message and getattr(message, 'successful_payment', None)


class _CombinedFilter(FilterBase):
    """Filtro combinado."""
    
    def __init__(self, operator: str, filters: List[FilterType]):
        self.operator = operator
        self.filters = filters
    
    def check(self, update: Any) -> bool:
        if self.operator == "AND":
            return all(f.check(update) for f in self.filters)
        else:
            return any(f.check(update) for f in self.filters)


class _NotFilter(FilterBase):
    """Filtro negado."""
    
    def __init__(self, filter_obj: FilterType):
        self.filter_obj = filter_obj
    
    def check(self, update: Any) -> bool:
        return not self.filter_obj.check(update)


__all__ = ["FiltersAdapter", "FilterBase"]
