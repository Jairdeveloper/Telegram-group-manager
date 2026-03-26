"""Shared rendering helpers for menu titles and sections."""

from typing import Iterable, Optional


def build_section(label: str, value: str) -> str:
    """Return a simple section line like 'Label: Value'."""
    return f"{label}: {value}"


def build_title(base_title: str, lines: Optional[Iterable[str]] = None) -> str:
    """Compose a menu title from a base title and extra lines."""
    content = [base_title]
    if lines:
        for line in lines:
            if line:
                content.append(line)
    return "\n".join(content)

