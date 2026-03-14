"""Bridge para convertir Update PTB a formato interno."""

from typing import Any, Dict, Optional

try:
    from telegram import Update
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    Update = None


class UpdateBridge:
    """Convierte Update de PTB a formato interno de la app."""
    
    @staticmethod
    def to_internal(update: Any) -> Dict[str, Any]:
        """Convierte Update PTB a diccionario interno.
        
        Args:
            update: Update de PTB
            
        Returns:
            Diccionario con formato interno
        """
        if not HAS_TELEGRAM or update is None:
            return {"update_id": 0}
        
        result = {
            "update_id": update.update_id,
        }
        
        if hasattr(update, 'message') and update.message:
            from robot_ptb_compat.bridge.message_bridge import MessageBridge
            result["message"] = MessageBridge.to_internal(update.message)
        
        if hasattr(update, 'edited_message') and update.edited_message:
            from robot_ptb_compat.bridge.message_bridge import MessageBridge
            result["edited_message"] = MessageBridge.to_internal(update.edited_message)
        
        if hasattr(update, 'callback_query') and update.callback_query:
            from robot_ptb_compat.bridge.callback_bridge import CallbackBridge
            result["callback_query"] = CallbackBridge.to_internal(update.callback_query)
        
        if hasattr(update, 'inline_query') and update.inline_query:
            result["inline_query"] = UpdateBridge._inline_query_to_internal(update.inline_query)
        
        if hasattr(update, 'chosen_inline_result') and update.chosen_inline_result:
            result["chosen_inline_result"] = UpdateBridge._chosen_inline_result_to_internal(update.chosen_inline_result)
        
        if hasattr(update, 'channel_post') and update.channel_post:
            from robot_ptb_compat.bridge.message_bridge import MessageBridge
            result["channel_post"] = MessageBridge.to_internal(update.channel_post)
        
        return result
    
    @staticmethod
    def _inline_query_to_internal(inline_query: Any) -> Dict[str, Any]:
        """Convierte InlineQuery a formato interno."""
        return {
            "id": inline_query.id,
            "from": UpdateBridge._user_to_internal(inline_query.from_user) if hasattr(inline_query, 'from_user') else None,
            "query": inline_query.query,
            "offset": inline_query.offset,
            "chat_type": inline_query.chat_type if hasattr(inline_query, 'chat_type') else None,
        }
    
    @staticmethod
    def _chosen_inline_result_to_internal(chosen: Any) -> Dict[str, Any]:
        """Convierte ChosenInlineResult a formato interno."""
        return {
            "result_id": chosen.result_id,
            "from": UpdateBridge._user_to_internal(chosen.from_user) if hasattr(chosen, 'from_user') else None,
            "query": chosen.query if hasattr(chosen, 'query') else None,
        }
    
    @staticmethod
    def _user_to_internal(user: Any) -> Optional[Dict[str, Any]]:
        """Convierte User a formato interno."""
        if user is None:
            return None
        return {
            "id": user.id,
            "is_bot": user.is_bot,
            "first_name": user.first_name,
            "last_name": user.last_name if hasattr(user, 'last_name') else None,
            "username": user.username if hasattr(user, 'username') else None,
            "language_code": user.language_code if hasattr(user, 'language_code') else None,
        }
    
    @staticmethod
    def from_internal(data: Dict[str, Any]) -> Any:
        """Convierte diccionario interno a Update PTB.
        
        Args:
            data: Diccionario en formato interno
            
        Returns:
            Update de PTB (si está disponible)
        """
        if not HAS_TELEGRAM:
            return None
        
        return Update.de_json(data, None)


__all__ = ["UpdateBridge"]
