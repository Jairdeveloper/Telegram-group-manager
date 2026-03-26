"""Bridge para convertir User PTB a formato interno."""

from typing import Any, Dict, Optional

try:
    from telegram import User
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    User = None


class UserBridge:
    """Convierte User de PTB a formato interno de la app."""
    
    @staticmethod
    def to_internal(user: Any) -> Optional[Dict[str, Any]]:
        """Convierte User PTB a diccionario interno.
        
        Args:
            user: User de PTB
            
        Returns:
            Diccionario con formato interno
        """
        if not HAS_TELEGRAM or user is None:
            return None
        
        return {
            "id": user.id,
            "is_bot": user.is_bot,
            "first_name": user.first_name,
            "last_name": user.last_name if hasattr(user, 'last_name') else None,
            "username": user.username if hasattr(user, 'username') else None,
            "language_code": user.language_code if hasattr(user, 'language_code') else None,
            "is_premium": user.is_premium if hasattr(user, 'is_premium') else None,
            "added_to_attachment_menu": user.added_to_attachment_menu if hasattr(user, 'added_to_attachment_menu') else None,
            "can_join_groups": user.can_join_groups if hasattr(user, 'can_join_groups') else None,
            "can_read_all_group_messages": user.can_read_all_group_messages if hasattr(user, 'can_read_all_group_messages') else None,
            "supports_inline_queries": user.supports_inline_queries if hasattr(user, 'supports_inline_queries') else None,
        }
    
    @staticmethod
    def from_internal(data: Dict[str, Any]) -> Optional[Any]:
        """Convierte diccionario interno a User PTB.
        
        Args:
            data: Diccionario en formato interno
            
        Returns:
            User de PTB (si está disponible)
        """
        if not HAS_TELEGRAM:
            return None
        
        if data is None:
            return None
        
        return User(
            id=data.get("id", 0),
            is_bot=data.get("is_bot", False),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name"),
            username=data.get("username"),
            language_code=data.get("language_code"),
        )
    
    @staticmethod
    def to_simple_dict(user: Any) -> Optional[Dict[str, int]]:
        """Convierte User a diccionario simple con solo id.
        
        Args:
            user: User de PTB
            
        Returns:
            Diccionario simple {"id": ...}
        """
        if user is None:
            return None
        return {"id": user.id}


__all__ = ["UserBridge"]
