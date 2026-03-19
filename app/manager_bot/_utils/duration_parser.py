"""Duration parsing helpers."""

from typing import Optional
import re


_UNIT_SECONDS = {
    "s": 1,
    "sec": 1,
    "secs": 1,
    "second": 1,
    "seconds": 1,
    "seg": 1,
    "segs": 1,
    "segundo": 1,
    "segundos": 1,
    "m": 60,
    "min": 60,
    "mins": 60,
    "minute": 60,
    "minutes": 60,
    "minuto": 60,
    "minutos": 60,
    "h": 3600,
    "hr": 3600,
    "hrs": 3600,
    "hour": 3600,
    "hours": 3600,
    "hora": 3600,
    "horas": 3600,
    "d": 86400,
    "day": 86400,
    "days": 86400,
    "dia": 86400,
    "dias": 86400,
    "w": 604800,
    "week": 604800,
    "weeks": 604800,
    "semana": 604800,
    "semanas": 604800,
    "mo": 2592000,
    "mon": 2592000,
    "month": 2592000,
    "months": 2592000,
    "mes": 2592000,
    "meses": 2592000,
    "y": 31536000,
    "yr": 31536000,
    "year": 31536000,
    "years": 31536000,
    "ano": 31536000,
    "anos": 31536000,
}


def parse_duration_to_seconds(text: str) -> Optional[int]:
    """Parse duration text into seconds.

    Accepts formats like:
    - "15 minutes"
    - "2h 30m"
    - "3 months 2 days 12 hours 4 minutes 34 seconds"
    - "45" (seconds)
    """
    if not text:
        return None
    normalized = text.strip().lower()
    if not normalized:
        return None

    tokens = re.findall(r"(\\d+)\\s*([a-zA-Z]+)?", normalized)
    if not tokens:
        return None

    total = 0
    for value_str, unit in tokens:
        try:
            value = int(value_str)
        except ValueError:
            return None

        if not unit:
            total += value
            continue

        unit = unit.lower()
        multiplier = _UNIT_SECONDS.get(unit)
        if multiplier is None:
            return None
        total += value * multiplier

    return total if total > 0 else None
