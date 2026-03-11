"""Telemetry module for ManagerBot."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class Telemetry:
    """Centralized telemetry for ManagerBot modules."""

    def __init__(self):
        self._metrics: Dict[str, Any] = {}

    def record_event(
        self,
        module: str,
        event: str,
        level: str = "INFO",
        **kwargs,
    ) -> None:
        """Record an event from a module."""
        event_data = {
            "module": module,
            "event": event,
            "level": level,
            "data": kwargs,
        }
        self._metrics.setdefault(module, []).append(event_data)
        logger.info(
            f"telemetry.{module}.{event}",
            extra=event_data,
        )

    def record_command(
        self,
        module: str,
        command: str,
        status: str,
        user_id: int = None,
        chat_id: int = None,
    ) -> None:
        """Record a command execution."""
        self.record_event(
            module=module,
            event=f"command.{command}",
            level="INFO",
            status=status,
            user_id=user_id,
            chat_id=chat_id,
        )

    def record_error(
        self,
        module: str,
        error: str,
        context: Dict[str, Any] = None,
    ) -> None:
        """Record an error from a module."""
        self.record_event(
            module=module,
            event="error",
            level="ERROR",
            error=error,
            context=context or {},
        )

    def get_module_events(self, module: str) -> list:
        """Get all events for a module."""
        return self._metrics.get(module, [])

    def get_all_events(self) -> Dict[str, list]:
        """Get all recorded events."""
        return self._metrics.copy()

    def clear(self) -> None:
        """Clear all recorded events."""
        self._metrics.clear()


_telemetry = None


def get_telemetry() -> Telemetry:
    """Get the global telemetry instance."""
    global _telemetry
    if _telemetry is None:
        _telemetry = Telemetry()
    return _telemetry


def record_module_event(
    module: str,
    event: str,
    level: str = "INFO",
    **kwargs,
) -> None:
    """Convenience function to record an event."""
    get_telemetry().record_event(module, event, level, **kwargs)
