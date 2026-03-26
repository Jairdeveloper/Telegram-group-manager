from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List


SUPPORTED_EXTENSIONS = {".md", ".txt", ".rst"}


def iter_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return
    for path in root.rglob("*"):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def load_text_files(paths: List[Path]) -> Dict[str, str]:
    documents: Dict[str, str] = {}
    for path in paths:
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            content = path.read_text(encoding="latin-1")
        documents[str(path)] = content
    return documents
