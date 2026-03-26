"""Helpers propios de la aplicación robot."""

import re
from typing import Any, Dict, Optional


def parse_command(text: str) -> tuple[Optional[str], list[str]]:
    """Parsea un comando de texto.
    
    Args:
        text: Texto del mensaje
        
    Returns:
        Tupla (comando, argumentos)
    """
    if not text or not text.strip().startswith('/'):
        return None, []
    
    parts = text.strip()[1:].split(maxsplit=1)
    command = parts[0].lower() if parts else None
    args = parts[1].split() if len(parts) > 1 else []
    
    return command, args


def extract_chat_id(update: Dict[str, Any]) -> Optional[int]:
    """Extrae el chat_id de un update.
    
    Args:
        update: Diccionario del update
        
    Returns:
        chat_id o None
    """
    if update.get("message"):
        return update["message"].get("chat", {}).get("id")
    if update.get("callback_query"):
        return update["callback_query"].get("message", {}).get("chat", {}).get("id")
    if update.get("edited_message"):
        return update["edited_message"].get("chat", {}).get("id")
    return None


def extract_user_id(update: Dict[str, Any]) -> Optional[int]:
    """Extrae el user_id de un update.
    
    Args:
        update: Diccionario del update
        
    Returns:
        user_id o None
    """
    if update.get("message"):
        return update["message"].get("from", {}).get("id")
    if update.get("callback_query"):
        return update["callback_query"].get("from", {}).get("id")
    if update.get("edited_message"):
        return update["edited_message"].get("from", {}).get("id")
    return None


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """Sanitiza texto para enviar a Telegram.
    
    Args:
        text: Texto a sanitizar
        max_length: Longitud máxima opcional
        
    Returns:
        Texto sanitizado
    """
    if not text:
        return ""
    
    text = text.strip()
    
    if max_length and len(text) > max_length:
        text = text[:max_length - 3] + "..."
    
    return text


def build_keyboard(buttons: list[list[Dict[str, str]]]) -> Dict[str, Any]:
    """Construye un teclado inline.
    
    Args:
        buttons: Lista de filas de botones
        
    Returns:
        Diccionario del teclado
    """
    return {
        "inline_keyboard": buttons
    }


__all__ = [
    "parse_command",
    "extract_chat_id",
    "extract_user_id",
    "sanitize_text",
    "build_keyboard",
]
