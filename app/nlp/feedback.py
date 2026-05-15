"""Feedback mechanism for NLP command understanding."""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class FallbackFeedback:
    """Feedback for a fallback event."""
    original_text: str
    fallback_reason: str
    timestamp: str
    user_id: Optional[int] = None
    chat_id: Optional[int] = None
    resolved: bool = False
    resolution_intent: Optional[str] = None


class NLPFeedbackManager:
    """Manager for NLP feedback from admins."""
    
    def __init__(self):
        self._fallback_history: List[FallbackFeedback] = []
        self._unresolved_count = 0
        self._common_patterns: Dict[str, int] = {}
    
    def record_fallback(
        self,
        original_text: str,
        fallback_reason: str,
        user_id: Optional[int] = None,
        chat_id: Optional[int] = None,
    ) -> None:
        """Record a fallback event."""
        feedback = FallbackFeedback(
            original_text=original_text,
            fallback_reason=fallback_reason,
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            chat_id=chat_id,
        )
        self._fallback_history.append(feedback)
        self._unresolved_count += 1
        
        pattern_key = f"{fallback_reason}:{original_text[:30]}"
        self._common_patterns[pattern_key] = self._common_patterns.get(pattern_key, 0) + 1
        
        logger.info(f"Fallback recorded: {fallback_reason} for '{original_text[:50]}'")
    
    def record_resolution(self, original_text: str, resolved_intent: str) -> bool:
        """Record that a fallback was resolved."""
        for i, fb in enumerate(reversed(self._fallback_history)):
            if fb.original_text == original_text and not fb.resolved:
                fb.resolved = True
                fb.resolution_intent = resolved_intent
                self._unresolved_count -= 1
                logger.info(f"Fallback resolved: {resolved_intent} for '{original_text[:50]}'")
                return True
        return False
    
    def get_unresolved_fallbacks(self) -> List[FallbackFeedback]:
        """Get all unresolved fallback events."""
        return [fb for fb in self._fallback_history if not fb.resolved]
    
    def get_common_patterns(self, top_n: int = 10) -> List[Dict]:
        """Get most common fallback patterns."""
        sorted_patterns = sorted(
            self._common_patterns.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [
            {"pattern": p[0], "count": p[1]}
            for p in sorted_patterns[:top_n]
        ]
    
    def get_fallback_summary(self) -> Dict:
        """Get summary of fallback events."""
        total = len(self._fallback_history)
        resolved = total - self._unresolved_count
        
        return {
            "total_fallbacks": total,
            "resolved": resolved,
            "unresolved": self._unresolved_count,
            "resolution_rate": round(resolved / total * 100, 1) if total > 0 else 0,
            "timestamp": datetime.now().isoformat(),
        }
    
    def generate_admin_suggestion(self, original_text: str) -> str:
        """Generate suggestion message for admin."""
        suggestions = []
        
        if any(word in original_text.lower() for word in ["bienvenida", "welcome"]):
            suggestions.append("Prueba: 'activar bienvenida' o 'cambiar mensaje de bienvenida'")
        
        if any(word in original_text.lower() for word in ["antiflood", "flood", "mensajes"]):
            suggestions.append("Prueba: 'activar antiflood' o 'pon antiflood con 5 mensajes en 3 segundos'")
        
        if any(word in original_text.lower() for word in ["filtro", "bloquear", "spam"]):
            suggestions.append("Prueba: 'bloquear palabra [palabra]' o 'quitar palabra [palabra]'")
        
        if any(word in original_text.lower() for word in ["estado", "status", "como esta"]):
            suggestions.append("Prueba: 'ver estado' o 'como esta el bot'")
        
        if any(word in original_text.lower() for word in ["ayuda", "help", "comandos"]):
            suggestions.append("Prueba: 'ayudame' o 'que puedes hacer'")
        
        if not suggestions:
            suggestions.append("Usa comandos explícitos como: 'activar [función]', 'ver [configuración]'")
        
        return "No entendí. " + " | ".join(suggestions)


_feedback_manager: Optional[NLPFeedbackManager] = None


def get_feedback_manager() -> NLPFeedbackManager:
    """Get or create feedback manager singleton."""
    global _feedback_manager
    if _feedback_manager is None:
        _feedback_manager = NLPFeedbackManager()
    return _feedback_manager


def record_fallback(
    text: str,
    reason: str,
    user_id: Optional[int] = None,
    chat_id: Optional[int] = None,
) -> None:
    """Record a fallback event."""
    get_feedback_manager().record_fallback(text, reason, user_id, chat_id)


def get_suggestion(text: str) -> str:
    """Get admin suggestion for unrecognized text."""
    return get_feedback_manager().generate_admin_suggestion(text)
