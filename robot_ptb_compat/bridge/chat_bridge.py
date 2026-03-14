"""Bridge para convertir Chat PTB a formato interno."""

from typing import Any, Dict, Optional

try:
    from telegram import Chat
    HAS_TELEGRAM = True
except ImportError:
    HAS_TELEGRAM = False
    Chat = None


class ChatBridge:
    """Convierte Chat de PTB a formato interno de la app."""
    
    @staticmethod
    def to_internal(chat: Any) -> Optional[Dict[str, Any]]:
        """Convierte Chat PTB a diccionario interno.
        
        Args:
            chat: Chat de PTB
            
        Returns:
            Diccionario con formato interno
        """
        if not HAS_TELEGRAM or chat is None:
            return None
        
        return {
            "id": chat.id,
            "type": chat.type,
            "title": chat.title if hasattr(chat, 'title') else None,
            "username": chat.username if hasattr(chat, 'username') else None,
            "first_name": chat.first_name if hasattr(chat, 'first_name') else None,
            "last_name": chat.last_name if hasattr(chat, 'last_name') else None,
            "is_forum": chat.is_forum if hasattr(chat, 'is_forum') else False,
            "photo": ChatBridge._photo_to_internal(chat.photo) if hasattr(chat, 'photo') and chat.photo else None,
            "active_usernames": chat.active_usernames if hasattr(chat, 'active_usernames') else None,
            "emoji_status_custom_emoji_id": chat.emoji_status_custom_emoji_id if hasattr(chat, 'emoji_status_custom_emoji_id') else None,
            "bio": chat.bio if hasattr(chat, 'bio') else None,
            "has_private_forwards": chat.has_private_forwards if hasattr(chat, 'has_private_forwards') else None,
            "has_restricted_voice_and_video_messages": chat.has_restricted_voice_and_video_messages if hasattr(chat, 'has_restricted_voice_and_video_messages') else None,
            "join_to_send_messages": chat.join_to_send_messages if hasattr(chat, 'join_to_send_messages') else None,
            "join_by_request": chat.join_by_request if hasattr(chat, 'join_by_request') else None,
            "description": chat.description if hasattr(chat, 'description') else None,
            "invite_link": chat.invite_link if hasattr(chat, 'invite_link') else None,
            "pinned_message": chat.pinned_message if hasattr(chat, 'pinned_message') else None,
            "permissions": ChatBridge._permissions_to_internal(chat.permissions) if hasattr(chat, 'permissions') and chat.permissions else None,
            "slow_mode_delay": chat.slow_mode_delay if hasattr(chat, 'slow_mode_delay') else None,
            "message_auto_delete_time": chat.message_auto_delete_time if hasattr(chat, 'message_auto_delete_time') else None,
            "has_aggressive_anti_spam_enabled": chat.has_aggressive_anti_spam_enabled if hasattr(chat, 'has_aggressive_anti_spam_enabled') else None,
            "has_hidden_members": chat.has_hidden_members if hasattr(chat, 'has_hidden_members') else None,
        }
    
    @staticmethod
    def _photo_to_internal(photo: Any) -> Optional[Dict[str, Any]]:
        """Convierte ChatPhoto."""
        if photo is None:
            return None
        return {
            "small_file_id": photo.small_file_id,
            "small_file_unique_id": photo.small_file_unique_id,
            "big_file_id": photo.big_file_id,
            "big_file_unique_id": photo.big_file_unique_id,
        }
    
    @staticmethod
    def _permissions_to_internal(permissions: Any) -> Optional[Dict[str, Any]]:
        """Convierte ChatPermissions."""
        if permissions is None:
            return None
        return {
            "can_send_messages": permissions.can_send_messages,
            "can_send_media_messages": permissions.can_send_media_messages,
            "can_send_polls": permissions.can_send_polls,
            "can_send_other_messages": permissions.can_send_other_messages,
            "can_add_web_page_previews": permissions.can_add_web_page_previews,
            "can_change_info": permissions.can_change_info,
            "can_invite_users": permissions.can_invite_users,
            "can_pin_messages": permissions.can_pin_messages,
            "can_manage_topics": permissions.can_manage_topics if hasattr(permissions, 'can_manage_topics') else None,
        }
    
    @staticmethod
    def from_internal(data: Dict[str, Any]) -> Optional[Any]:
        """Convierte diccionario interno a Chat PTB.
        
        Args:
            data: Diccionario en formato interno
            
        Returns:
            Chat de PTB (si está disponible)
        """
        if not HAS_TELEGRAM:
            return None
        
        if data is None:
            return None
        
        return Chat(
            id=data.get("id", 0),
            type=data.get("type", "private"),
            title=data.get("title"),
            username=data.get("username"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
        )
    
    @staticmethod
    def to_simple_dict(chat: Any) -> Optional[Dict[str, int]]:
        """Convierte Chat a diccionario simple con solo id.
        
        Args:
            chat: Chat de PTB
            
        Returns:
            Diccionario simple {"id": ...}
        """
        if chat is None:
            return None
        return {"id": chat.id}


__all__ = ["ChatBridge"]
