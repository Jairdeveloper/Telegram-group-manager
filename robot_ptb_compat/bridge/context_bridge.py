"""Bridge para convertir CallbackContext PTB a formato interno."""

from typing import Any, Dict, Optional

try:
    from telegram.ext import CallbackContext
    HAS_TELEGRAM_EXT = True
except ImportError:
    HAS_TELEGRAM_EXT = False
    CallbackContext = None


class ContextBridge:
    """Convierte CallbackContext de PTB a formato interno de la app."""
    
    @staticmethod
    def to_internal(context: Any) -> Dict[str, Any]:
        """Convierte CallbackContext PTB a diccionario interno.
        
        Args:
            context: CallbackContext de PTB
            
        Returns:
            Diccionario con formato interno
        """
        if not HAS_TELEGRAM_EXT or context is None:
            return {}
        
        from robot_ptb_compat.bridge.user_bridge import UserBridge
        from robot_ptb_compat.bridge.chat_bridge import ChatBridge
        
        result = {
            "args": list(context.args) if hasattr(context, 'args') and context.args else [],
            "matches": ContextBridge._matches_to_internal(context.matches) if hasattr(context, 'matches') and context.matches else None,
        }
        
        if hasattr(context, 'bot') and context.bot:
            result["bot"] = {
                "id": context.bot.id,
                "username": context.bot.username if hasattr(context.bot, 'username') else None,
                "first_name": context.bot.first_name if hasattr(context.bot, 'first_name') else None,
            }
        
        if hasattr(context, 'bot_data'):
            result["bot_data"] = dict(context.bot_data) if context.bot_data else {}
        
        if hasattr(context, 'chat_data'):
            result["chat_data"] = dict(context.chat_data) if context.chat_data else {}
        
        if hasattr(context, 'user_data'):
            result["user_data"] = dict(context.user_data) if context.user_data else {}
        
        if hasattr(context, 'job'):
            result["job"] = ContextBridge._job_to_internal(context.job) if context.job else None
        
        if hasattr(context, 'error'):
            result["error"] = str(context.error) if context.error else None
        
        if hasattr(context, 'async_executor'):
            result["async_executor"] = True
        
        return result
    
    @staticmethod
    def _matches_to_internal(matches: Any) -> Optional[list]:
        """Convierte matches de regex."""
        if matches is None:
            return None
        result = []
        for match in matches:
            if hasattr(match, 'groups'):
                result.append({
                    "groups": match.groups(),
                    "groupdict": match.groupdict(),
                })
            else:
                result.append(str(match))
        return result
    
    @staticmethod
    def _job_to_internal(job: Any) -> Optional[Dict[str, Any]]:
        """Convierte Job."""
        if job is None:
            return None
        return {
            "name": job.name if hasattr(job, 'name') else None,
            "callback": str(job.callback) if hasattr(job, 'callback') else None,
            "data": job.data if hasattr(job, 'data') else None,
            "next_t": job.next_t.isoformat() if hasattr(job, 'next_t') and job.next_t else None,
        }
    
    @staticmethod
    def from_internal(data: Dict[str, Any], context: Any = None) -> Any:
        """Crea un contexto interno desde diccionario.
        
        Args:
            data: Diccionario en formato interno
            context: CallbackContext original de PTB (opcional)
            
        Returns:
            Diccionario con formato interno simplificado
        """
        if data is None:
            return {}
        
        return {
            "args": data.get("args", []),
            "chat_id": data.get("chat_id"),
            "user_id": data.get("user_id"),
            "message_id": data.get("message_id"),
            "data": data.get("data", {}),
        }
    
    @staticmethod
    def extract_chat_id(context: Any) -> Optional[int]:
        """Extrae chat_id del contexto.
        
        Args:
            context: CallbackContext de PTB
            
        Returns:
            chat_id o None
        """
        if context is None:
            return None
        
        if hasattr(context, 'effective_chat') and context.effective_chat:
            return context.effective_chat.id
        
        if hasattr(context, 'chat_data'):
            for chat_id in context.chat_data.keys():
                return chat_id
        
        return None
    
    @staticmethod
    def extract_user_id(context: Any) -> Optional[int]:
        """Extrae user_id del contexto.
        
        Args:
            context: CallbackContext de PTB
            
        Returns:
            user_id o None
        """
        if context is None:
            return None
        
        if hasattr(context, 'effective_user') and context.effective_user:
            return context.effective_user.id
        
        if hasattr(context, 'user_data'):
            for user_id in context.user_data.keys():
                return user_id
        
        return None
    
    @staticmethod
    def extract_message_id(context: Any) -> Optional[int]:
        """Extrae message_id del contexto.
        
        Args:
            context: CallbackContext de PTB
            
        Returns:
            message_id o None
        """
        if context is None:
            return None
        
        if hasattr(context, 'effective_message') and context.effective_message:
            return context.effective_message.message_id
        
        return None


__all__ = ["ContextBridge"]
