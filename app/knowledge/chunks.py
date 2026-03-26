from __future__ import annotations

from typing import List


def chunk_text(text: str, max_chars: int = 1000, overlap: int = 100) -> List[str]:
    text = (text or "").strip()
    if not text:
        return []

    if max_chars <= 0:
        return [text]

    chunks: List[str] = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + max_chars, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= length:
            break
        start = max(0, end - overlap)
    return chunks
