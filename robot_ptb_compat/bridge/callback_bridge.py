"""Bridge para convertir CallbackQuery PTB a formato interno."""

from typing import Any, Dict, Optional

try:
    from telegram import CallbackQuery
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    CallbackQuery = None


class CallbackBridge:
    """Convierte CallbackQuery de PTB a formato interno de la app."""
    
    @staticmethod
    def to_internal(callback_query: Any) -> Dict[str, Any]:
        """Convierte CallbackQuery PTB a diccionario interno.
        
        Args:
            callback_query: CallbackQuery de PTB
            
        Returns:
            Diccionario con formato interno
        """
        if not HAS_TELEGRAM or callback_query is None:
            return {}
        
        from robot_ptb_compat.bridge.user_bridge import UserBridge
        from robot_ptb_compat.bridge.chat_bridge import ChatBridge
        from robot_ptb_compat.bridge.message_bridge import MessageBridge
        
        result = {
            "id": callback_query.id,
            "from": UserBridge.to_internal(callback_query.from_user) if hasattr(callback_query, 'from_user') else None,
            "chat_instance": callback_query.chat_instance if hasattr(callback_query, 'chat_instance') else None,
            "data": callback_query.data if hasattr(callback_query, 'data') else None,
            "game_short_name": callback_query.game_short_name if hasattr(callback_query, 'game_short_name') else None,
        }
        
        if hasattr(callback_query, 'message') and callback_query.message:
            result["message"] = CallbackBridge._message_to_internal(callback_query.message)
        
        return result
    
    @staticmethod
    def _message_to_internal(message: Any) -> Optional[Dict[str, Any]]:
        """Convierte Message contenido en CallbackQuery."""
        if message is None:
            return None
        
        from robot_ptb_compat.bridge.message_bridge import MessageBridge
        from robot_ptb_compat.bridge.chat_bridge import ChatBridge
        from robot_ptb_compat.bridge.user_bridge import UserBridge
        
        result = {
            "message_id": message.message_id,
            "date": message.date.isoformat() if hasattr(message, 'date') and message.date else None,
            "chat": ChatBridge.to_internal(message.chat) if hasattr(message, 'chat') and message.chat else None,
            "from": UserBridge.to_internal(message.from_user) if hasattr(message, 'from_user') and message.from_user else None,
        }
        
        if hasattr(message, 'text'):
            result["text"] = message.text
        
        if hasattr(message, 'caption'):
            result["caption"] = message.caption
        
        if hasattr(message, 'reply_markup') and message.reply_markup:
            result["reply_markup"] = MessageBridge._keyboard_to_internal(message.reply_markup)
        
        return result
    
    @staticmethod
    def from_internal(data: Dict[str, Any]) -> Optional[Any]:
        """Convierte diccionario interno a CallbackQuery PTB.
        
        Args:
            data: Diccionario en formato interno
            
        Returns:
            CallbackQuery de PTB (si está disponible)
        """
        if not HAS_TELEGRAM:
            return None
        
        if data is None:
            return None
        
        from telegram import User, Chat, Message
        
        user_data = data.get("from", {})
        user = User(
            id=user_data.get("id", 0),
            is_bot=user_data.get("is_bot", False),
            first_name=user_data.get("first_name", ""),
        ) if user_data else None
        
        chat_data = data.get("message", {}).get("chat", {})
        chat = Chat(
            id=chat_data.get("id", 0),
            type=chat_data.get("type", "private"),
        ) if chat_data else None
        
        return CallbackQuery(
            id=data.get("id", ""),
            from_user=user,
            chat_instance=data.get("chat_instance", ""),
            data=data.get("data"),
        )


__all__ = ["CallbackBridge"]
